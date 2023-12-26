from django.conf import settings
from django.db import models


class AuditableMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditorsMixin(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class PublishableMixin(models.Model):
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField()

    def is_draft(self):
        return not self.is_published

    class Meta:
        abstract = True


class PublisherMixin(models.Model):
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        abstract = True
