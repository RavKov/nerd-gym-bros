import datetime
import logging

import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import connection, transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from gymApi.access import (
    get_exercise_for_user,
    get_workout_day_log_for_user,
    get_workout_item_log_for_user,
    get_workout_set_log_for_user,
)
from gymApi.serializers import (
    BugReportSerializer,
    ClientProfileSerializer,
    EquipmentSerializer,
    ExerciseSerializer,
    GymSerializer,
    MobileTextContentSerializer,
    NewFeatureRequestSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    VerifyEmailSerializer,
    WorkoutDayDetailedLogSerializer,
    WorkoutItemDetailedLogSerializer,
    WorkoutPlanRunSerializer,
    WorkoutPlanSerializer,
)
from gymApi.throttling import RegisterRateThrottle
from gymApp.models import (
    ClientProfile,
    EmailVerificationCode,
    Equipment,
    Exercise,
    Gym,
    MobileTextContent,
    Subscription,
    SubscriptionPayment,
    SubscriptionPlan,
    WorkoutDay,
    WorkoutDayLog,
    WorkoutItem,
    WorkoutItemLog,
    WorkoutPlan,
    WorkoutPlanRun,
    WorkoutSetLog,
)

logger = logging.getLogger(__name__)


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


class HealthCheckAPI(APIView):
    """Liveness/readiness probe for Docker and load balancers."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request: Request):
        try:
            connection.ensure_connection()
            db_ok = True
        except Exception:
            logger.exception("Health check: database connection failed")
            db_ok = False

        payload = {
            "status": "ok" if db_ok else "degraded",
            "database": "ok" if db_ok else "unavailable",
        }
        http_status = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(payload, status=http_status)


class SubscriptionPlanListAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        subscription_plans = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(subscription_plans, many=True)
        return Response(serializer.data)


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


class WorkoutPlanListAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        client = ClientProfile.objects.get(user=request.user)
        subscription_plan = client.subscription_plan
        if not subscription_plan:
            return Response(
                [],
                status=status.HTTP_204_NO_CONTENT,
            )
        workout_plans = client.subscription_plan.workout_plans.all()
        serializer = WorkoutPlanSerializer(workout_plans, many=True)
        return Response(serializer.data)


class WorkoutPlanRunAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        client = ClientProfile.objects.get(user=request.user)
        workout_plan_run = get_active_workout_plan_run(client)
        if not workout_plan_run:
            return Response(
                {"detail": "No active workout plan run."},
                status=status.HTTP_204_NO_CONTENT,
            )
        serializer = WorkoutPlanRunSerializer(workout_plan_run)
        return Response(serializer.data)

    def patch(self, request: Request):
        logger.info(f">>> WorkoutPlanRunAPI PATCH data: {request.data}")
        client = ClientProfile.objects.get(user=request.user)
        workout_plan_run = get_active_workout_plan_run(client)
        if not workout_plan_run:
            logger.info(">>> WorkoutPlanRunAPI PATCH no active workout plan run")
            client.active_workout_plan = None
            client.save(update_fields=["active_workout_plan"])
            return Response(
                {"detail": "No active workout plan run."},
                status=status.HTTP_204_NO_CONTENT,
            )

        is_active = request.data.get("is_active", None)
        finished_at = request.data.get("finished_at", None)
        if is_active is not None and not is_active:
            workout_plan_run.is_active = is_active
            workout_plan_run.finished_at = finished_at
            if not finished_at:
                workout_plan_run.finished_at = timezone.now()
            workout_plan_run.save(update_fields=["is_active", "finished_at"])
            logger.info(f">>> WorkoutPlanRunAPI PATCH updated: {request.data}")
            client.active_workout_plan = None
            client.save(update_fields=["active_workout_plan"])

            return Response({"message": "Workout plan run updated."}, status=status.HTTP_200_OK)
        logger.info(f">>> WorkoutPlanRunAPI PATCH INVALID data: {request.data}")

        return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)


class WorkoutDayDetailedLogAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, pk: int):
        workout_day_log = get_workout_day_log_for_user(request.user, pk)
        serializer = WorkoutDayDetailedLogSerializer(workout_day_log)
        return Response(serializer.data)

    def patch(self, request: Request, pk: int):
        completed = request.data.get("completed", None)
        if completed is not None:
            workout_day_log = get_workout_day_log_for_user(request.user, pk)
            workout_day_log.completed = completed
            workout_day_log.save(update_fields=["completed"])
            return Response({"message": "Workout day log updated."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)


class WorkoutItemDetailedLogAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, pk: int):
        workout_item_log = get_workout_item_log_for_user(request.user, pk)
        serializer = WorkoutItemDetailedLogSerializer(workout_item_log)
        return Response(serializer.data)

    def patch(self, request: Request, pk: int):
        completed = request.data.get("completed", None)
        if completed is not None:
            workout_item_log = get_workout_item_log_for_user(request.user, pk)
            workout_item_log.completed = completed
            workout_item_log.save(update_fields=["completed"])
            return Response({"message": "Workout item log updated."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_set_log(request: Request, pk: int):
    actual_amount = request.data.get("actual_amount", None)

    if actual_amount is not None:
        workout_set_log = get_workout_set_log_for_user(request.user, pk)
        workout_set_log.actual_amount = actual_amount
        workout_set_log.save(update_fields=["actual_amount"])
        return Response({"message": "Workout set log updated."}, status=status.HTTP_200_OK)
    return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)


def get_active_workout_plan_run(client: ClientProfile) -> WorkoutPlanRun | None:
    timezone.now()
    return WorkoutPlanRun.objects.filter(
        client=client,
        is_active=True,
    ).first()


def create_workout_plan_run_for_client(
    client: ClientProfile, workout_plan: WorkoutPlan
) -> WorkoutPlanRun:
    workout_plan_run = WorkoutPlanRun.objects.create(
        client=client, workout_plan=workout_plan, started_at=timezone.now()
    )

    workout_plan_days = WorkoutDay.objects.filter(workout_plan=workout_plan).order_by("day_number")
    planned_day_date = timezone.now().date()

    for day in workout_plan_days:
        day_log = WorkoutDayLog.objects.create(
            workout_plan_run=workout_plan_run,
            workout_day=day,
            date=planned_day_date,
            completed=False,
        )
        planned_day_date += datetime.timedelta(days=1)

        workout_items = WorkoutItem.objects.filter(workout_day=day)

        for item in workout_items:
            item_log = WorkoutItemLog.objects.create(
                workout_day_log=day_log,
                workout_item=item,
            )

            for s in range(item.sets):
                WorkoutSetLog.objects.create(
                    workout_item_log=item_log,
                    set_number=s + 1,
                )
        # day_log = workout_plan_run.day_logs.create(
        #     workout_day=day,
        #     completed=False,
        # )

    logger.info(f">>> Created WorkoutPlanRun {workout_plan_run.id} for user {client.user.username}")
    return workout_plan_run


class WorkoutPlanChooseAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        workout_plan = WorkoutPlan.objects.get(pk=request.data.get("workout_plan_id"))

        client = ClientProfile.objects.get(user=request.user)
        client.active_workout_plan = workout_plan
        client.save()

        previous_run = get_active_workout_plan_run(client)

        if previous_run:
            previous_run.is_active = False
            previous_run.finished_at = timezone.now()
            previous_run.save(update_fields=["is_active", "finished_at"])

        workout_plan_run = create_workout_plan_run_for_client(client, workout_plan)

        logger.info(
            f">>> User {request.user.username} chose workout plan {workout_plan.name} | created WorkoutPlanRun {workout_plan_run.id}"
        )
        return Response({"message": "Workout plan updated."}, status=status.HTTP_200_OK)


class ExerciseListAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        client = ClientProfile.objects.get(user=request.user)
        if not client.subscription_plan:
            return Response(
                [],
                status=status.HTTP_204_NO_CONTENT,
            )

        exercises = Exercise.objects.filter(
            workoutitem__workout_day__workout_plan__subscriptionplan=client.subscription_plan
        ).distinct()

        serializer = ExerciseSerializer(exercises, many=True)
        return Response(serializer.data)


class ExerciseDetailUpdateDeleteAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, pk: int):
        exercise = get_exercise_for_user(request.user, pk)
        serializer = ExerciseSerializer(exercise)
        return Response(serializer.data)

    def put(self, request: Request, pk: int):
        exercise = get_exercise_for_user(request.user, pk)
        serializer = ExerciseSerializer(exercise, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk: int):
        exercise = get_exercise_for_user(request.user, pk)
        exercise.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def _send_verification_email(to_email: str, code: str) -> None:
    try:
        send_mail(
            subject="Verify your email",
            message=f"Your verification code is: {code}\nIt expires in 15 minutes.",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@gymapp.local"),
            recipient_list=[to_email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error("Failed to send verification email to %s: %s", to_email, e)
    else:
        logger.info("Verification email sent to %s", to_email)


class RegisterAPI(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def post(self, request: Request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        user = s.save()
        _, code = EmailVerificationCode.issue_for_user(user=user, ttl_minutes=15)
        _send_verification_email(user.email, code)

        return Response(
            {
                "message": "Account created. Please verify your email.",
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        s = VerifyEmailSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data["email"]
        code = s.validated_data["code"]

        user = request.user
        if user.email != email:
            logger.error(
                f">>> VerifyEmailAPI: email mismatch for user {user.username}: {user.email} != {email}"
            )
            return Response(
                {"detail": "Email does not match the authenticated user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ok = EmailVerificationCode.verify(user=user, code=code)
        if not ok:
            logger.error(
                f">>> VerifyEmailAPI: invalid code for user {user.username} with email {email}"
            )
            return Response(
                {"detail": "Invalid code or expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = ClientProfile.objects.get(user=user)
        if not profile.verified:
            profile.verified = True
            profile.save(update_fields=["verified"])

        return Response({"message": "Email verified."}, status=status.HTTP_200_OK)


class ResendVerificationAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        s = ResendVerificationSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        email = s.validated_data["email"]

        user = request.user
        logger.info(f">>> ResendVerificationAPI called for user {user.username} with email {email}")
        if user.email != email:
            return Response(
                {"detail": "Email does not match the authenticated user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = ClientProfile.objects.get(user=user)
        if profile.verified:
            return Response({"message": "Email already verified."}, status=status.HTTP_200_OK)

        _, code = EmailVerificationCode.issue_for_user(user=user, ttl_minutes=15)
        _send_verification_email(user.email, code)

        return Response({"message": "Verification code sent."}, status=status.HTTP_200_OK)


class ClientDetailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        user = request.user
        client_profile = ClientProfile.objects.get(user=user)

        serializer = ClientProfileSerializer(client_profile)
        return Response(serializer.data)


class BugReportAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        serializer = BugReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bug_report = serializer.save(user=request.user)
        logger.info(f">>> User {request.user.username} reported a bug with id {bug_report.id}")

        return Response(
            {"message": "Bug report submitted successfully."},
            status=status.HTTP_201_CREATED,
        )


class NewFeatureRequestAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        serializer = NewFeatureRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        feature_request = serializer.save(user=request.user)
        logger.info(
            f">>> User {request.user.username} requested a new feature with id {feature_request.id}"
        )

        return Response(
            {"message": "Feature request submitted successfully."},
            status=status.HTTP_201_CREATED,
        )


class GymListAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        gyms = Gym.objects.all()
        serializer = GymSerializer(gyms, many=True)
        return Response(serializer.data)


class EquipmentListAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        equipments = Equipment.objects.all()
        serializer = EquipmentSerializer(equipments, many=True)
        return Response(serializer.data)


# STRIPE

stripe.api_key = settings.STRIPE_SECRET_KEY


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
        s = Subscription.objects.create(
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
            f">>> Created subscription {s.stripe_subscription_id} for user {request.user.username}"
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

    # 1) subskrypcja zaktualizowana
    if event["type"] == "customer.subscription.updated":
        logger.info(">>> stripe_webhook: customer.subscription.updated event")
        data = event["data"]["object"]
        latest_sub_item = _get_latest_subscription_item(data)
        try:
            sub = Subscription.objects.get(stripe_subscription_id=data["id"])
            sub.status = data["status"]
            sub.current_period_end = _datetime_from_stripe_timestamp(
                latest_sub_item["current_period_end"]
            )
            sub.save()
        except Subscription.DoesNotExist:
            pass

    # 2) opłacona faktura
    if event["type"] == "invoice.paid":
        logger.info(">>> stripe_webhook: invoice.paid event")
        invoice = event["data"]["object"]
        sub_id = _get_stripe_subscription_id_from_invoice(invoice)
        # sub_id = invoice["subscription"]
        try:
            sub = Subscription.objects.get(stripe_subscription_id=sub_id)
            SubscriptionPayment.objects.update_or_create(
                stripe_invoice_id=invoice["id"],
                defaults={
                    "subscription": sub,
                    "amount_paid": invoice["amount_paid"],
                    "currency": invoice["currency"],
                    "paid_at": _datetime_from_stripe_timestamp(invoice["created"]),
                },
            )
        except Subscription.DoesNotExist:
            pass

    return Response(status=200)


class MobileTextContentListAPI(APIView):
    """
    GET: Pobierz wszystkie teksty (lub filtruj po group).

    Public read-only CMS copy for the mobile app (AllowAny by design).
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        group = request.query_params.get("group", None)
        if group:
            contents = MobileTextContent.objects.filter(group=group)
        else:
            contents = MobileTextContent.objects.all()
        serializer = MobileTextContentSerializer(contents, many=True)
        return Response(serializer.data)


class MobileTextContentCreateAPI(APIView):
    """
    POST: Utwórz nowy tekst (wymaga admin)
    """

    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = MobileTextContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MobileTextContentDetailAPI(APIView):
    """
    GET: Pobierz tekst po kodzie (publiczny).

    Public read-only CMS copy for the mobile app (AllowAny by design).
    """

    permission_classes = [permissions.AllowAny]

    def get_object(self, code):
        try:
            return MobileTextContent.objects.get(code=code)
        except MobileTextContent.DoesNotExist:
            return None

    def get(self, request, code):
        obj = self.get_object(code)
        if not obj:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MobileTextContentSerializer(obj)
        return Response(serializer.data)


class MobileTextContentUpdateDeleteAPI(APIView):
    """
    PUT: Aktualizuj tekst (wymaga admin)
    DELETE: Usuń tekst (wymaga admin)
    """

    permission_classes = [permissions.IsAdminUser]

    def get_object(self, code):
        try:
            return MobileTextContent.objects.get(code=code)
        except MobileTextContent.DoesNotExist:
            return None

    def put(self, request, code):
        obj = self.get_object(code)
        if not obj:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MobileTextContentSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):
        obj = self.get_object(code)
        if not obj:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
