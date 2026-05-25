from rest_framework import permissions

from gymApi.serializers import EquipmentSerializer
from gymApp.models import Equipment

from .pagination import PaginatedAPIView


class EquipmentListAPI(PaginatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        equipments = Equipment.objects.order_by("id")
        return self.paginate_response(request, equipments, EquipmentSerializer)
