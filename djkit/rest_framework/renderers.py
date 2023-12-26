from collections.abc import Iterable, Mapping

from rest_framework.renderers import JSONRenderer as BaseJsonRenderer


class JSONRenderer(BaseJsonRenderer):
    def render_success(self, data, accepted_media_type=None, renderer_context=None):
        return data

    def render_errors(self, data, accepted_media_type=None, renderer_context=None):
        field_errors = {}
        non_field_errors = []

        if isinstance(data, Mapping):
            field_errors = data

        elif isinstance(data, Iterable):  # not mapping
            non_field_errors = data

        return {
            "field_errors": field_errors,
            "non_field_errors": non_field_errors,
        }

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context and renderer_context.get("response", None):
            response = renderer_context["response"]
            if response.status_code >= 400:
                data = self.render_errors(data, accepted_media_type, renderer_context)
            else:
                data = self.render_success(data, accepted_media_type, renderer_context)

        return super().render(data, accepted_media_type, renderer_context)
