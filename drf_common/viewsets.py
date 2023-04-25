from typing import Mapping

from rest_framework import viewsets


class MultiPermissionViewSet(viewsets.ModelViewSet):
    permission_classes_retrieve = None
    permission_classes_list = None
    permission_classes_create = None
    permission_classes_update = None
    permission_classes_destroy = None

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
            "partial_update": self.permission_classes_update,
            "destroy": self.permission_classes_destroy,
            "retrieve": self.permission_classes_retrieve,
            "list": self.permission_classes_list,
        }

    def get_permissions(self):
        return [
            perm()
            for perm in self.get_action_perms_map().get(
                self.action, self.permission_classes
            )
        ]
