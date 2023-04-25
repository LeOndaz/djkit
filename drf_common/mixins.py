from rest_framework import status
from rest_framework.mixins import CreateModelMixin as BaseCreateModelMixin
from rest_framework.mixins import UpdateModelMixin as BaseUpdateModelMixin
from rest_framework.response import Response


class CommonCreateModelMixin(BaseCreateModelMixin):
    def create(self, request, *args, **kwargs):
        input_serializer = self.get_input_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        instance = self.perform_create(input_serializer)
        output_serializer = self.get_output_serializer(instance)
        headers = self.get_success_headers(input_serializer.data)
        return Response(
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save()


class CommonUpdateModelMixin(BaseUpdateModelMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        input_serializer = self.get_input_serializer(
            instance, data=request.data, partial=partial
        )
        input_serializer.is_valid(raise_exception=True)
        self.perform_update(input_serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        output_serializer = self.get_output_serializer(instance)
        return Response(output_serializer.data)

    def perform_update(self, serializer):
        """
        Must return the instance saved from the serializer
        """
        return serializer.save()


class MultiSerializerMixin:
    """Can take in input_serializer & output_serializer in update or create. So the request body doesn't have to match
    the response body.
    """

    input_serializer_class = None
    output_serializer_class = None

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