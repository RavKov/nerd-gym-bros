from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from gymApi.serializers import MobileTextContentSerializer
from gymApp.models import MobileTextContent


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
