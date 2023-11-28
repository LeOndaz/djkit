from inspect import isclass
from typing import Callable, Dict

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .utils import validate_row_with_serializer


class RecursiveSerializer(serializers.Serializer):
    """A serializer that can be used to recursively serialize an object."""

    def to_representation(self, value):
        """
        :param value: A serializer object, maybe a ListSerializer or a Serializer
        :return: the data from that serializer
        """
        if isinstance(self.parent, serializers.ListSerializer):
            return self.parent.parent.to_representation(value)

        return self.parent.to_representation(value)


class EnumSerializer(serializers.BaseSerializer):
    """A serializer for enums

    :param enum: The enum to serialize
    :type enum: instance of enum.Enum

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


class IOSerializer(serializers.Serializer):
    """
    Input/Output serializer is used when having different formats for request/response.

    user_serializer = IOSerializer(
            input_serializer=PrimaryKeyRelatedField(),
            output_serializer=UserSerializer()
        )

    In the response, you'll find the user object, but in the request, you'll only send the PK.
    """

    def __init__(self, input_serializer, output_serializer, **kwargs):
        self.input_serializer = input_serializer
        self.output_serializer = output_serializer

        super().__init__(**kwargs, required=False)

    def bind(self, field_name, parent):
        self.input_serializer.bind(field_name, parent)
        self.output_serializer.bind(field_name, parent)
        super().bind(field_name, parent)

    def to_representation(self, instance):
        return self.output_serializer.to_representation(instance)

    def to_internal_value(self, data):
        return self.input_serializer.to_internal_value(data)

    def get_fields(self):
        # being used as output
        if hasattr(self, "initial_data"):
            return self.output_serializer.get_fields()

        return self.input_serializer.get_fields()


class TableUploadField(serializers.FileField):
    """
    A field for handling TabularUploads in any library like Pandas or Pola.rs.

    Usage:

    class MyTableUploadField(TableUploadField):
        default_format_handlers = {
            "csv": pd.read_csv,
        }

    And usage as expected

    class MySerializerNeedingTableUpload(serializers.Serializer):
        my_csv = MyTableUploadField(required=True)

        def create(self, validated_data):
            dataframe = validated_data['my_csv']

        def validate_my_csv_row(self, row, index, table_df):
            # process row as needed and return it, or raise!
            # if you return None, return value won't be used.

            return row
    """

    default_error_messages = {
        **serializers.FileField.default_error_messages,
        "row": _("row {row} is invalid: {message}"),
        "invalid_format": _("received an unexpected format={format}"),
        "format_handler": _("the format handler raised an error"),
    }

    default_format_handlers = {
        "csv": None,
    }

    def __init__(self, row_validator=None, **kwargs):
        assert (
            "write_only" not in kwargs
        ), "serializer {} is already write_only by default".format(
            self.__class__.__name__
        )

        assert list(
            self.default_format_handlers.items()
        ), "must at some format_handlers using your favourite library like pola.rs or pandas"
        super().__init__(**kwargs, write_only=True)
        self.row_validator = row_validator
        self.allowed_upload_formats = self.default_format_handlers.keys()

    def get_row_validator(self):
        if isinstance(self.row_validator, str):
            method = getattr(self.parent, self.row_validator, None)

            if method is None:
                raise AssertionError(
                    "method {} doesn't exist on serializer {}".format(
                        self.row_validator,
                        self.parent.__class__.__name__,
                    )
                )

            return method

        if isclass(self.row_validator) and not issubclass(
            self.row_validator, serializers.Serializer
        ):
            raise ValidationError(
                "validate_row accepts only subclasses of rest_framework.serializers.Serializer"
            )

        if isclass(self.row_validator) and issubclass(
            self.row_validator, serializers.Serializer
        ):
            return validate_row_with_serializer(self.row_validator, self.context)

        if self.row_validator is None:
            method_name = "validate_{}_row".format(self.field_name)
            return getattr(self.parent, method_name, None)

        raise AssertionError(
            "validate_row can only be of types str, callable or a subclass of serializers.Serializer"
            " but got={}".format(type(self.row_validator).__name__)
        )

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        self.row_validator = self.get_row_validator()

    def fail(self, key, **kwargs):
        if key == "row":
            assert "row" in kwargs, "must pass cell in kwargs when key=row"
            assert "message" in kwargs, "must pass a message for errors in rows"

            row = kwargs["row"]
            message = kwargs["message"]

            raise ValidationError(
                {
                    "original_exception": message,
                    "message": "Error in cell",
                    "row": row,
                },
                code="TABLE_ROW_ERROR",
            )

        return super().fail(key, **kwargs)

    def get_format_handlers(self) -> Dict[str, Callable]:
        if not any(self.default_format_handlers.values()):
            raise ValueError("{}.get_format_handlers returned no handlers")

        return self.default_format_handlers

    def _format_handler(self, file):
        file_name = file.name
        upload_format = file_name.rsplit(".")[1]
        format_handler = self.get_format_handlers().get(upload_format)

        try:
            return format_handler(file)
        except Exception as e:
            self.fail("format_handler", message=str(e))

    def to_internal_value(self, file):
        super().to_internal_value(file)

        table_object = self._format_handler(file)

        if self.row_validator:
            for i, row in table_object.iterrows():
                try:
                    new_value = self.row_validator(row, i, table_object)
                except serializers.ValidationError as e:
                    raise ValidationError(
                        {
                            "field_errors": e.detail,
                            "row": i + 1,
                        }
                    )

                if new_value is not None:
                    table_object.iloc[i] = new_value

        return table_object

    def to_representation(self, value):
        raise ValidationError(
            "{} is a write_only field".format(self.__class__.__name__)
        )
