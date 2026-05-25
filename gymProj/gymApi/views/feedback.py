import logging

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from gymApi.serializers import BugReportSerializer, NewFeatureRequestSerializer

logger = logging.getLogger(__name__)


class BugReportAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
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

    def post(self, request):
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
