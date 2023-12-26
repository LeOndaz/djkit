from typing import Mapping

from rest_framework import viewsets
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)


class GenericViewSet(viewsets.GenericViewSet):
    """A ViewSet that adds support for per-action permissions"""

    permission_classes_retrieve = []
    permission_classes_list = []
    permission_classes_create = []
    permission_classes_update = []
    permission_classes_destroy = []

    # fallback, permissions for all actions
    permission_classes = []

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
        """Tries to find the action in the return value of self.get_action_perms_map & if it's not found, it tries to get
        a variable named permission_classes_<action> & if there's none, the action has no permissions.

        Example:

        @action(detail=True)
        def eat(self, request, pk=None):
            pass

        This action has many ways of passing permissions, in the action decorator as usual, or override get_action_perms_map
        or add a variable named permission_classes_eat

        """
        action = self.action
        action_perms_map = self.get_action_perms_map()

        if action in action_perms_map:
            action_perms = action_perms_map[action]
        else:
            action_perms = self.permission_classes

        return [perm() for perm in action_perms]


class ModelViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """
    A replacement for `restframework.viewsets.ModelViewSet`
    """

    pass
