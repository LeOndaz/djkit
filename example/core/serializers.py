from rest_framework import serializers

from djkit.rest_framework.serializers import EnumSerializer, RecursiveSerializer

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


class CategorySerializer(serializers.ModelSerializer):
    parent = RecursiveSerializer()

    class Meta:
        model = models.Category
        fields = "__all__"
