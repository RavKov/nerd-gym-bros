import datetime
import logging

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from gymApi.serializers import SubscriptionPlanSerializer, SubscriptionSerializer
from gymApp.models import ClientProfile, Subscription, SubscriptionPayment, SubscriptionPlan

from .pagination import PaginatedAPIView
from .workouts import get_active_workout_plan_run

logger = logging.getLogger(__name__)

INACTIVE_SUBSCRIPTION_STATUSES = {"canceled", "unpaid"}


def _stripe_value(source, key: str, default=None):
    if isinstance(source, dict):
        return source.get(key, default)
    return getattr(source, key, default)


def _get_latest_subscription_item(stripe_subscription) -> dict | object | None:
    items = _stripe_value(stripe_subscription, "items", {}) or {}
    data = _stripe_value(items, "data", []) or []

    if data:
        data = sorted(data, key=lambda x: _stripe_value(x, "created", 0), reverse=True)
        return data[0]
    return None


def _datetime_from_stripe_timestamp(ts) -> timezone.datetime | None:
    if not ts:
        return None
    if isinstance(ts, int):
        return timezone.datetime.fromtimestamp(ts, tz=datetime.UTC)
    return None


def _get_stripe_subscription_id_from_invoice(invoice: dict) -> str | None:
    """Getting subscription from invoice is weird: https://docs.stripe.com/api/invoice-line-item/object"""
    stripe_sub_id = invoice.get("subscription")
    if stripe_sub_id:
        return stripe_sub_id
    lines = invoice.get("lines") or {}
    data = lines.get("data") or []

    for line in data:
        parent = (line or {}).get("parent") or {}
        details = parent.get("subscription_item_details") or {}
        sub_id = details.get("subscription")
        if sub_id:
            return sub_id
    return None


def _clear_client_subscription_state(client: ClientProfile) -> None:
    update_fields = []
    if client.subscription_plan_id is not None:
        client.subscription_plan = None
        update_fields.append("subscription_plan")
    if client.active_workout_plan_id is not None:
        client.active_workout_plan = None
        update_fields.append("active_workout_plan")
    if update_fields:
        client.save(update_fields=update_fields)

    current_workout_run = get_active_workout_plan_run(client)
    if current_workout_run:
        current_workout_run.is_active = False
        current_workout_run.finished_at = timezone.now()
        current_workout_run.save(update_fields=["is_active", "finished_at"])


def _assign_client_subscription_plan_for_subscription(subscription: Subscription) -> None:
    client = ClientProfile.objects.filter(user=subscription.user).first()
    if not client:
        logger.warning("Stripe sync: missing client profile for user %s", subscription.user_id)
        return

    subscription_plan = SubscriptionPlan.objects.filter(
        stripe_price_id=subscription.price_id
    ).first()
    if not subscription_plan:
        logger.warning(
            "Stripe sync: no subscription plan configured for price_id %s",
            subscription.price_id,
        )
        return

    if client.subscription_plan_id != subscription_plan.id:
        client.subscription_plan = subscription_plan
        client.save(update_fields=["subscription_plan"])


def _get_requested_subscription_plan(request: Request) -> SubscriptionPlan:
    subscription_plan_id = request.data.get("subscription_plan_id")
    if subscription_plan_id is not None:
        return get_object_or_404(SubscriptionPlan, pk=subscription_plan_id)

    price_id = request.data.get("price_id")
    if not price_id:
        raise ValueError("subscription_plan_id or price_id is required.")

    try:
        return SubscriptionPlan.objects.get(stripe_price_id=price_id)
    except SubscriptionPlan.DoesNotExist as exc:
        raise LookupError("No subscription plan configured for the provided price_id.") from exc


def _configure_stripe_api_key() -> bool:
    if not settings.STRIPE_SECRET_KEY:
        return False
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return True


class SubscriptionPlanListAPI(PaginatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        subscription_plans = SubscriptionPlan.objects.order_by("id")
        return self.paginate_response(request, subscription_plans, SubscriptionPlanSerializer)


class SubscriptionPlanChooseAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        subscription_plan = get_object_or_404(
            SubscriptionPlan,
            pk=request.data.get("subscription_plan_id"),
        )
        if subscription_plan.stripe_price_id:
            return Response(
                {
                    "detail": "Paid subscription plans must be activated through Stripe payment flow."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        client = ClientProfile.objects.get(user=request.user)
        client.subscription_plan = subscription_plan
        client.save()
        logger.info(
            "User %s chose free subscription plan %s",
            request.user.username,
            subscription_plan.name,
        )
        return Response({"message": "Subscription plan updated."}, status=status.HTTP_200_OK)

    def get(self, request: Request):
        client_profile = ClientProfile.objects.get(user=request.user)
        subscription_plan = client_profile.subscription_plan
        serializer = SubscriptionPlanSerializer(subscription_plan)
        return Response(serializer.data)


class SubscriptionDetailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        subscription = Subscription.objects.filter(user=request.user, status="active").last()
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)


def get_or_create_stripe_customer_id(client: ClientProfile) -> str:
    if client.stripe_customer_id:
        return client.stripe_customer_id

    customer = stripe.Customer.create(email=client.user.email)
    client.stripe_customer_id = customer.id
    client.save(update_fields=["stripe_customer_id"])
    return customer.id


class CreateSubscriptionSheetAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not _configure_stripe_api_key():
            return Response(
                {"detail": "Stripe is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            subscription_plan = _get_requested_subscription_plan(request)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except LookupError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        if not subscription_plan.stripe_price_id:
            return Response(
                {"detail": "Selected subscription plan does not require Stripe payment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        price_id = subscription_plan.stripe_price_id

        customer_id = get_or_create_stripe_customer_id(ClientProfile.objects.get(user=request.user))

        stripe_subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.confirmation_secret"],
        )

        latest_sub_item = _get_latest_subscription_item(stripe_subscription)
        logger.info(
            "Created Stripe subscription %s for customer %s and plan %s",
            stripe_subscription.id,
            customer_id,
            subscription_plan.id,
        )
        subscription = Subscription.objects.create(
            user=request.user,
            stripe_customer_id=customer_id,
            stripe_subscription_id=stripe_subscription.id,
            price_id=price_id,
            status=_stripe_value(stripe_subscription, "status"),
            current_period_start=_datetime_from_stripe_timestamp(
                _stripe_value(latest_sub_item, "current_period_start")
            ),
            current_period_end=_datetime_from_stripe_timestamp(
                _stripe_value(latest_sub_item, "current_period_end")
            ),
            cancel_at_period_end=bool(
                _stripe_value(stripe_subscription, "cancel_at_period_end", False)
            ),
            canceled_at=_datetime_from_stripe_timestamp(
                _stripe_value(stripe_subscription, "canceled_at")
            ),
            ended_at=_datetime_from_stripe_timestamp(
                _stripe_value(stripe_subscription, "ended_at")
            ),
        )
        logger.info(
            "Created local subscription %s for user %s",
            subscription.stripe_subscription_id,
            request.user.username,
        )
        ephemeral_key = stripe.EphemeralKey.create(
            customer=customer_id,
            stripe_version="2023-10-16",
        )

        client_secret = stripe_subscription.latest_invoice.confirmation_secret.client_secret

        return Response(
            {
                "clientSecret": client_secret,
                "customerId": customer_id,
                "ephemeralKey": ephemeral_key.secret,
            }
        )


class CancelSubscriptionAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        client = ClientProfile.objects.get(user=request.user)
        subscription_plan = client.subscription_plan

        if not subscription_plan:
            return Response(
                {"detail": "No active subscription to cancel."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not subscription_plan.stripe_price_id:
            _clear_client_subscription_state(client)

            return Response(
                {"detail": "Free subscription plan, nothing to cancel."},
                status=status.HTTP_200_OK,
            )

        subscription = Subscription.objects.filter(user=request.user).last()
        if not subscription:
            return Response(
                {"detail": "No active subscription to cancel."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not _configure_stripe_api_key():
            return Response(
                {"detail": "Stripe is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        stripe.Subscription.delete(subscription.stripe_subscription_id)
        subscription.status = "canceled"
        subscription.save(update_fields=["status"])
        _clear_client_subscription_state(client)
        return Response(
            {"detail": "Subscription canceled successfully."},
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])  # webhook nie ma JWT
def stripe_webhook(request):
    if not settings.STRIPE_WEBHOOK_SECRET:
        return Response(
            {"detail": "Stripe webhook secret is not configured."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        return Response(status=400)
    except stripe.error.SignatureVerificationError:
        return Response(status=400)

    if event["type"] == "customer.subscription.updated":
        data = event["data"]["object"]
        latest_sub_item = _get_latest_subscription_item(data)
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=data["id"])
            subscription.status = data["status"]
            subscription.current_period_end = _datetime_from_stripe_timestamp(
                _stripe_value(latest_sub_item, "current_period_end")
            )
            subscription.current_period_start = _datetime_from_stripe_timestamp(
                _stripe_value(latest_sub_item, "current_period_start")
            )
            subscription.cancel_at_period_end = bool(data.get("cancel_at_period_end", False))
            subscription.canceled_at = _datetime_from_stripe_timestamp(data.get("canceled_at"))
            subscription.ended_at = _datetime_from_stripe_timestamp(data.get("ended_at"))
            subscription.save(
                update_fields=[
                    "status",
                    "current_period_end",
                    "current_period_start",
                    "cancel_at_period_end",
                    "canceled_at",
                    "ended_at",
                ]
            )
            client = ClientProfile.objects.filter(user=subscription.user).first()
            if client and subscription.status in INACTIVE_SUBSCRIPTION_STATUSES:
                _clear_client_subscription_state(client)
        except Subscription.DoesNotExist:
            pass

    if event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        sub_id = _get_stripe_subscription_id_from_invoice(invoice)
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=sub_id)
            SubscriptionPayment.objects.update_or_create(
                stripe_invoice_id=invoice["id"],
                defaults={
                    "subscription": subscription,
                    "amount_paid": invoice["amount_paid"],
                    "currency": invoice["currency"],
                    "paid_at": _datetime_from_stripe_timestamp(invoice["created"]),
                },
            )
            _assign_client_subscription_plan_for_subscription(subscription)
        except Subscription.DoesNotExist:
            pass

    return Response(status=200)
