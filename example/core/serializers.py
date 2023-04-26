from rest_framework import serializers

from django_rest_commons import EnumSerializer

from . import models


class HumanSerializer(serializers.ModelSerializer):
    level = EnumSerializer(enum=models.Human.Level)
    military_status = EnumSerializer(enum=models.Human.MilitaryStatus)

    class Meta:
        model = models.Human
        fields = [
            "id",
            "level",
            "military_status",
        ]
