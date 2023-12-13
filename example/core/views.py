from rest_framework import serializers
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from commonkit.rest_framework.renderers import JSONRenderer
from commonkit.rest_framework.serializers import DebugSerializer, IOSerializer
from commonkit.rest_framework.viewsets import ModelViewSet

from .models import Human
from .serializers import HumanSerializer

TRUTHY_VALUES = ["1", "True", "true"]


class HumanViewSet(ModelViewSet):
    queryset = Human.objects.all()
    serializer_class = HumanSerializer

    permission_classes_create = [IsAdminUser]
    permission_classes_destroy = [IsAdminUser]
    permission_classes_update = [IsAdminUser]
    permission_classes_list = [IsAuthenticated]
    permission_classes_retrieve = [IsAuthenticated]


class IOSerializerDebugView(APIView):
    def get(self, request):
        serializer = IOSerializer(
            input_serializer=serializers.EmailField(),
            output_serializer=serializers.CharField(),
        )

        debug = DebugSerializer(serializer)
        return Response(data=debug.data)


class ImprovedJSONRendererView(RetrieveAPIView, CreateAPIView):
    renderer_classes = [JSONRenderer]
    serializer_class = HumanSerializer

    def get(self, request, *args, **kwargs):
        fail = request.query_params.get("fail", False) in TRUTHY_VALUES

        if fail:
            raise serializers.ValidationError("INTENTIONAL_FIELD_ERROR")

        return Response(data={"key": "value"})
