from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from gymApi.serializers import GymSerializer
from gymApp.models import Gym


class GymListAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        gyms = Gym.objects.all()
        serializer = GymSerializer(gyms, many=True)
        return Response(serializer.data)
