from typing import Mapping

from rest_framework import viewsets
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin

from .mixins import CommonCreateModelMixin, CommonUpdateModelMixin


class CommonViewSet(viewsets.GenericViewSet):
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
        """
        Tries to find the action in the return value of self.get_action_perms_map & if it's not found, it tries to get
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
        action_perms_on_klass = getattr(
            self, "permission_classes_{}".format(action), None
        )

        if action in action_perms_map:
            action_perms = action_perms_map[action]
        elif action_perms_on_klass:
            action_perms = action_perms_on_klass
        else:
            action_perms = []

        return [perm() for perm in action_perms]

    def get_output_serializer(self):
        """
        Returns the output serializer
        :return:
        """
        return self.output_serializer_class or self.serializer_class

    def get_input_serializer(self):
        """
        Returns the input serializer
        """
        return self.input_serializer_class or self.serializer_class


class ModelViewSet(
    CommonCreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    CommonUpdateModelMixin,
    DestroyModelMixin,
    CommonViewSet,
):
    pass
