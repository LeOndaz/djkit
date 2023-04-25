from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class RecursiveSerializer(serializers.Serializer):
    """A serializer that can be used to recursively serialize an object."""

    def to_representation(self, value):
        """
        :param value: A serializer object, maybe a ListSerializer or a Serializer
        :return: the data from that serializer
        """
        if isinstance(self.parent, serializers.ListSerializer):
            return self.parent.parent.__class__(value).data

        return self.parent.__class__(value).data


class EnumSerializer(serializers.BaseSerializer):
    """A serializer for enums

    :param enum: The enum to serialize
    :type enum: enum.Enum

    .. code-block:: python
        :caption: models.py

        class Human(models.Model):
            class Level(models.IntegerChoices):
                BEGINNER = 0
                INTERMEDIATE = 1
                ADVANCED = 2

            class MilitaryStatus(models.TextChoices):
                EXEMPTED = "exempted", "Exempted"
                SERVED = "served", "Served"
                POSTPONED = "postponed", "Postponed"


        name = models.CharField(max_length=128)
        level = models.IntegerField(choices=Level.choices)
        military_status = models.CharField(
            choices=MilitaryStatus.choices,
             max_length=128
         )

    .. code-block:: python
        :caption: serializers.py

        class HumanSerializer(serializers.ModelSerializer):
            level = EnumSerializer(enum=models.Human.Level)
            military_status = EnumSerializer(enum=models.Human.MilitaryStatus)

            class Meta:
                model = models.Human
                fields = [
                    'id',
                    'level',
                    'military_status',
                ]

    .. code-block:: python
        :caption: POST request example

        {
            "level": "BEGINNER",
            "MILITARY_STATUS": "EXEMPTED",
        }

    .. code-block:: python
        :caption: Response example

        {
            "id": 1,
            "level": "BEGINNER",
            "MILITARY_STATUS": "EXEMPTED"
        }

    - You don't have to deal with numbers if the enum is `django.db.models.IntegerChoices`

    - request.data expects any of BEGINNER, INTERMEDIATE or ADVANCED and it automatically translates it to numbers.

    - response.data automatically gets serialized from numbers to plain text.


    """

    def __init__(self, enum, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum = enum

    def to_internal_value(self, data):
        """
        :param data: the word like "BEGINNER"
        :return: the database equivalent to that word
        """
        return self.enum[data].value

    def to_representation(self, code):
        """
        :param code: The database equivalent format
        :return: The word equivalent to that number
        """
        for name, member in self.enum.__members__.items():
            if member.value == code:
                return name

        raise ValidationError(
            detail=f"code {code} has no corresponding value in enum {self.enum.__class__.__name__}"
        )
