from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from fires_watch.fires.api.serializers import FiresCalculateSerializer


class FiresViewSet(GenericViewSet):
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def calculate(self, request):
        serializer = FiresCalculateSerializer(
            context={"request": request}, data=request.data
        )
        if serializer.is_valid():
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.error_messages,
            )
