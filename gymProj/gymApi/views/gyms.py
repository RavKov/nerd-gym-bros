from rest_framework import permissions

from gymApi.serializers import GymSerializer
from gymApp.models import Gym

from .pagination import PaginatedAPIView


class GymListAPI(PaginatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        gyms = Gym.objects.all()
        return self.paginate_response(request, gyms, GymSerializer)
