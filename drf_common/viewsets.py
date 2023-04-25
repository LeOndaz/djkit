from typing import Mapping

from rest_framework import viewsets


class MultiPermissionViewSet(viewsets.ModelViewSet):
    permission_classes_create = []
    permission_classes_update = []
    permission_classes_destroy = []

    input_serializer_class = None
    output_serializer_class = None

    def get_action_perms_map(self) -> Mapping:
        """
        Returns a map of keys representing actions and values representing action permissions
        :return: dict
        """
        return {
            "create": self.permission_classes_create,
            "update": self.permission_classes_update,
            "destroy": self.permission_classes_destroy,
            "retrieve": self.permission_classes,
            "list": self.permission_classes,
        }

    def get_permissions(self):
        return [perm() for perm in self.get_action_perms_map().get(self.action, [])]
