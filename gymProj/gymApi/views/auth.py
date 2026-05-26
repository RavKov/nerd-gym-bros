import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import connection, transaction
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from gymApi.serializers import (
    ClientProfileSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    VerifyEmailSerializer,
)
from gymApi.throttling import RegisterRateThrottle
from gymApp.models import ClientProfile, EmailVerificationCode

logger = logging.getLogger(__name__)


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


def _send_verification_email(to_email: str, code: str) -> None:
    try:
        send_mail(
            subject="Verify your email",
            message=f"Your verification code is: {code}\nIt expires in 15 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
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
        from gymApi import views as views_package

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        _, code = EmailVerificationCode.issue_for_user(user=user, ttl_minutes=15)
        views_package._send_verification_email(user.email, code)

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
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

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
        from gymApi import views as views_package

        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

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
        views_package._send_verification_email(user.email, code)

        return Response({"message": "Verification code sent."}, status=status.HTTP_200_OK)


class ClientDetailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        client_profile = ClientProfile.objects.get(user=request.user)
        serializer = ClientProfileSerializer(client_profile)
        return Response(serializer.data)
