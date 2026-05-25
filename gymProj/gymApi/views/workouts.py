import datetime
import logging

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from gymApi.access import (
    get_workout_day_log_for_user,
    get_workout_item_log_for_user,
    get_workout_set_log_for_user,
)
from gymApi.serializers import (
    WorkoutDayDetailedLogSerializer,
    WorkoutItemDetailedLogSerializer,
    WorkoutPlanRunSerializer,
    WorkoutPlanSerializer,
)
from gymApp.models import (
    ClientProfile,
    WorkoutDay,
    WorkoutDayLog,
    WorkoutItem,
    WorkoutItemLog,
    WorkoutPlan,
    WorkoutPlanRun,
    WorkoutSetLog,
)

from .pagination import PaginatedAPIView

logger = logging.getLogger(__name__)


class WorkoutPlanListAPI(PaginatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        client = ClientProfile.objects.get(user=request.user)
        subscription_plan = client.subscription_plan
        if not subscription_plan:
            return self.paginate_response(
                request, WorkoutPlan.objects.none(), WorkoutPlanSerializer
            )
        workout_plans = client.subscription_plan.workout_plans.all()
        return self.paginate_response(request, workout_plans, WorkoutPlanSerializer)


class WorkoutPlanRunAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        client = ClientProfile.objects.get(user=request.user)
        workout_plan_run = get_active_workout_plan_run(client)
        if not workout_plan_run:
            return Response(
                {"detail": "No active workout plan run."},
                status=status.HTTP_404_NOT_FOUND,
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
                status=status.HTTP_404_NOT_FOUND,
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

        return Response({"detail": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)


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
        return Response({"detail": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)


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
        return Response({"detail": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_set_log(request: Request, pk: int):
    actual_amount = request.data.get("actual_amount", None)

    if actual_amount is not None:
        workout_set_log = get_workout_set_log_for_user(request.user, pk)
        workout_set_log.actual_amount = actual_amount
        workout_set_log.save(update_fields=["actual_amount"])
        return Response({"message": "Workout set log updated."}, status=status.HTTP_200_OK)
    return Response({"detail": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)


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

            for set_number in range(item.sets):
                WorkoutSetLog.objects.create(
                    workout_item_log=item_log,
                    set_number=set_number + 1,
                )

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
