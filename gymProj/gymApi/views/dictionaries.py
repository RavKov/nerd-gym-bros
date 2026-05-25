from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from gymApi.serializers import EquipmentSerializer
from gymApp.models import Equipment


class EquipmentListAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        equipments = Equipment.objects.all()
        serializer = EquipmentSerializer(equipments, many=True)
        return Response(serializer.data)
