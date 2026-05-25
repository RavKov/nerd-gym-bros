import datetime
import logging

import stripe
from django.conf import settings
from django.contrib.auth.models import User
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

stripe.api_key = settings.STRIPE_SECRET_KEY


def _get_latest_subscription_item(stripe_subscription: dict) -> dict | None:
    logger.info(f">>> _get_latest_subscription_item stripe_subscription: {stripe_subscription}")
    items = stripe_subscription.get("items", {})
    logger.info(f">>> _get_latest_subscription_item items: {items}")
    data = items.get("data", None) or []
    logger.info(f">>> _get_latest_subscription_item data: {data}")

    if data:
        data = sorted(data, key=lambda x: x.get("created", 0), reverse=True)
        return data[0]
    return None


def _datetime_from_stripe_timestamp(ts) -> timezone.datetime | None:
    if not ts:
        return None
    if isinstance(ts, int):
        return timezone.datetime.fromtimestamp(ts, tz=datetime.UTC)
    return None


def _resolve_user_by_stripe_customer_id(stripe_customer_id: str) -> User | None:
    if not stripe_customer_id:
        return None
    client = (
        ClientProfile.objects.filter(stripe_customer_id=stripe_customer_id)
        .select_related("user")
        .first()
    )
    return client.user if client else None


def _get_stripe_subscription_id_from_invoice(invoice: dict) -> str | None:
    """Getting subscription from invoice is weird: https://docs.stripe.com/api/invoice-line-item/object"""
    stripe_sub_id = invoice.get("subscription")
    if stripe_sub_id:
        return stripe_sub_id
    lines = invoice.get("lines") or {}
    logger.info(f"Looking for subscription id in invoice lines: {lines}")
    data = lines.get("data") or []
    logger.info(f"Invoice lines data: {data}")

    for line in data:
        sub_id = (line or {}).get("parent").get("subscription_item_details").get("subscription")
        if sub_id:
            return sub_id
    return None


class SubscriptionPlanListAPI(PaginatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        subscription_plans = SubscriptionPlan.objects.all()
        return self.paginate_response(request, subscription_plans, SubscriptionPlanSerializer)


class SubscriptionPlanChooseAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        # TODO - obsługa płatności jeśli płatna subskrypcja
        subscription_plan = SubscriptionPlan.objects.get(
            pk=request.data.get("subscription_plan_id")
        )

        client = ClientProfile.objects.get(user=request.user)
        client.subscription_plan = subscription_plan
        client.save()
        logger.info(
            f">>> User {request.user.username} chose subscription plan {subscription_plan.name}"
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
        price_id = request.data["price_id"]

        customer_id = get_or_create_stripe_customer_id(ClientProfile.objects.get(user=request.user))

        stripe_subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.confirmation_secret"],
        )

        latest_sub_item = _get_latest_subscription_item(stripe_subscription)
        logger.info(
            f">>>> Created Stripe subscription {stripe_subscription.id} for customer {customer_id} with price {price_id}, latest_sub_item: {latest_sub_item}"
        )
        subscription = Subscription.objects.create(
            user=request.user,
            stripe_customer_id=customer_id,
            stripe_subscription_id=stripe_subscription.id,
            price_id=price_id,
            status=stripe_subscription.status,
            current_period_start=_datetime_from_stripe_timestamp(
                getattr(latest_sub_item, "current_period_start", None)
            ),
            current_period_end=_datetime_from_stripe_timestamp(
                getattr(latest_sub_item, "current_period_end", None)
            ),
            cancel_at_period_end=bool(getattr(stripe_subscription, "cancel_at_period_end", False)),
            canceled_at=_datetime_from_stripe_timestamp(
                getattr(stripe_subscription, "canceled_at", None)
            ),
            ended_at=_datetime_from_stripe_timestamp(
                getattr(stripe_subscription, "ended_at", None)
            ),
        )
        logger.info(
            f">>> Created subscription {subscription.stripe_subscription_id} for user {request.user.username}"
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
            client.subscription_plan = None
            client.active_workout_plan = None
            client.save(update_fields=["subscription_plan", "active_workout_plan"])
            current_workout_run = get_active_workout_plan_run(client)
            if current_workout_run:
                current_workout_run.is_active = False
                current_workout_run.finished_at = timezone.now()
                current_workout_run.save(update_fields=["is_active", "finished_at"])

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
        stripe.Subscription.delete(subscription.stripe_subscription_id)
        subscription.status = "canceled"
        subscription.save(update_fields=["status"])
        client.subscription_plan = None
        client.active_workout_plan = None

        current_workout_run = get_active_workout_plan_run(client)
        if current_workout_run:
            current_workout_run.is_active = False
            current_workout_run.finished_at = timezone.now()
            current_workout_run.save(update_fields=["is_active", "finished_at"])

        client.save(update_fields=["subscription_plan", "active_workout_plan"])
        return Response(
            {"detail": "Subscription canceled successfully."},
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])  # webhook nie ma JWT
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return Response(status=400)

    if event["type"] == "customer.subscription.updated":
        logger.info(">>> stripe_webhook: customer.subscription.updated event")
        data = event["data"]["object"]
        latest_sub_item = _get_latest_subscription_item(data)
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=data["id"])
            subscription.status = data["status"]
            subscription.current_period_end = _datetime_from_stripe_timestamp(
                latest_sub_item["current_period_end"]
            )
            subscription.save()
        except Subscription.DoesNotExist:
            pass

    if event["type"] == "invoice.paid":
        logger.info(">>> stripe_webhook: invoice.paid event")
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
        except Subscription.DoesNotExist:
            pass

    return Response(status=200)
