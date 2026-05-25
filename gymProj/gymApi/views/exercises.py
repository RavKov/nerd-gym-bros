from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from gymApi.access import get_exercise_for_user
from gymApi.serializers import ExerciseSerializer
from gymApp.models import ClientProfile, Exercise


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
