from rest_framework.permissions import IsAdminUser, IsAuthenticated

from django_rest_commons import ModelViewSet

from .models import Human
from .serializers import HumanSerializer


class HumanViewSet(ModelViewSet):
    queryset = Human.objects.all()
    serializer_class = HumanSerializer

    permission_classes_create = [IsAdminUser]
    permission_classes_destroy = [IsAdminUser]
    permission_classes_update = [IsAdminUser]
    permission_classes_list = [IsAuthenticated]
    permission_classes_retrieve = [IsAuthenticated]
