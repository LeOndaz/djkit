import base64
import typing
from collections import abc
from enum import Enum
from inspect import isclass
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from commonkit.private import errors
from commonkit.private.utils import subject_to_change, validate_row_with_serializer
from commonkit.utils import Obfuscator


class RecursiveSerializer(serializers.Serializer):
    """A serializer that can be used to recursively serialize an object."""

    def to_representation(self, value):
        """
        :param value: A serializer object, maybe a ListSerializer or a Serializer
        :return: the data from that serializer
        """
        if self.parent is None:
            raise serializers.ValidationError(
                errors.serializer_cant_be_used_independently(self)
            )

        if isinstance(self.parent, serializers.ListSerializer):
            return self.parent.parent.to_representation(value)

        return self.parent.to_representation(value)


class EnumSerializer(serializers.BaseSerializer):
    """A serializer for enums to encourage the use of IntegerChoices for improving database performance

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
        assert issubclass(enum, Enum), errors.must_pass_enum_to_enum_serializer(enum)
        self.enum = enum

    def to_internal_value(self, data):
        """
        :param data: the word like "BEGINNER"
        :return: the database equivalent to that word in self.enum
        """
        try:
            return self.enum[data].value
        except KeyError:
            raise serializers.ValidationError(
                "non-existent key passed to EnumSerializer, available keys are [{}]".format(
                    ", ".join(self.allowed_inputs)
                )
            )

    def get_display(self, member):
        return member.value if isinstance(member.value, str) else member.name

    @property
    def allowed_inputs(self):
        return [self.get_display(member) for member in self.enum]

    def to_representation(self, code):
        """
        :param code: The database equivalent format
        :return: The word equivalent to that number
        """
        for member in self.enum:
            if member.value == code:
                return self.get_display(member)

        raise serializers.ValidationError(
            detail=f"code={code} has no corresponding value in enum {self.enum.__class__.__name__}"
        )


@subject_to_change
class IOSerializer(serializers.Serializer):
    """Input/Output serializer is used when having different formats for request/response.

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

    def to_representation(self, instance):
        return self.output_serializer.to_representation(instance)

    def to_internal_value(self, data):
        return self.input_serializer.to_internal_value(data)

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        self.input_serializer.bind(field_name, parent)
        self.output_serializer.bind(field_name, parent)

    def get_fields(self):
        request = self.context.get("request", None)

        if request is None:
            return self.output_serializer.get_fields()

        if request.method in ["POST", "PUT", "PATCH"]:
            if isinstance(self.input_serializer, serializers.Field):
                return {self.input_serializer.field_name: self.input_serializer}
            return self.input_serializer().get_fields()
        if isinstance(self.output_serializer, serializers.Field):
            return {self.output_serializer.field_name: self.output_serializer}
        return self.output_serializer().get_fields()


class TableUploadField(serializers.FileField):
    """A field for handling TabularUploads in any library like Pandas or Pola.rs.

    Usage:

    class MyTableUploadField(TableUploadField):
        handlers = {
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
            # return None if you only want to validate but don't to modify the table

            return row
    """

    default_error_messages = {
        **serializers.FileField.default_error_messages,
        "row": _("row {row} is invalid: {message}"),
        "invalid_format": _("received an unexpected format={format}"),
        "format_handler": _("the format handler raised an error"),
    }
    handlers = {}
    handler_kwargs = {}
    row_validator = None

    def _validate_handler_kwargs(self, handler_kwargs):
        if handler_kwargs:
            assert isinstance(
                handler_kwargs, abc.Mapping
            ), errors.handler_kwargs_must_be_mapping(self, handler_kwargs)

    def __init__(
        self,
        row_validator=None,
        handler_kwargs=None,
        **kwargs,
    ):
        assert "write_only" not in kwargs, errors.serializer_write_only_by_default(self)
        assert "read_only" not in kwargs, errors.serializer_cant_pass_ready_only(self)

        self._validate_handler_kwargs(handler_kwargs)
        self.handler_kwargs = handler_kwargs or {}
        self.row_validator = row_validator

        super().__init__(**kwargs, write_only=True)

    def get_row_validator(self):
        """return a function to validate each row, the function takes 3 arguments (row, i, table_object)"""
        if isinstance(self.row_validator, str):
            method = getattr(self.parent, self.row_validator, None)

            if method is None:
                raise serializers.ValidationError(
                    "method {} doesn't exist on serializer {}".format(
                        self.row_validator,
                        self.parent.__class__.__name__,
                    )
                )

            return method

        if isclass(self.row_validator) and not issubclass(
            self.row_validator, serializers.Serializer
        ):
            raise serializers.ValidationError(
                "validate_row accepts only subclasses of rest_framework.serializers.Serializer"
            )

        if isclass(self.row_validator) and issubclass(
            self.row_validator, serializers.Serializer
        ):
            return validate_row_with_serializer(self.row_validator, self.context)

        if self.row_validator is None:
            method_name = "validate_{}_row".format(self.field_name)
            return getattr(self.parent, method_name, None)

        raise serializers.ValidationError(
            "validate_row can only be of types str, callable or a subclass of serializers.Serializer"
            " but got={}".format(type(self.row_validator).__name__)
        )

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        self.row_validator = self.get_row_validator()

    def fail(self, key, **kwargs):
        if key == "row":
            assert "row" in kwargs, errors.must_pass_row_when_key_is_row()
            assert "message" in kwargs, errors.must_pass_message_when_key_is_row()

            row = kwargs["row"]
            message = kwargs["message"]

            raise serializers.ValidationError(
                {
                    "original_exception": message,
                    "message": "Error in row",
                    "row": row,
                },
                code="TABLE_ROW_ERROR",
            )

        return super().fail(key, **kwargs)

    @property
    def allowed_upload_formats(self):
        return tuple((self.get_format_handlers().keys()))

    def is_allowed_format(self, fmt):
        return fmt in self.allowed_upload_formats

    @classmethod
    def get_format_handlers(cls) -> typing.Mapping[str, typing.Callable]:
        """return a mapping of format:handler"""
        return cls.handlers

    @classmethod
    def get_format_handler(cls, file):
        """Return a handler for the provided file's format
        :param file: file object from django request
        """
        file_name = file.name
        upload_format = Path(file_name).suffix.removeprefix(".")
        handlers = cls.get_format_handlers()

        if upload_format not in handlers and "*" not in handlers:
            raise serializers.ValidationError(
                "a handler for format={} was not defined".format(upload_format)
            )

        handler = handlers[upload_format]

        if not callable(handler):
            raise serializers.ValidationError(
                "handler defined for {} is not callable".format(
                    upload_format,
                )
            )

        return handlers[upload_format]

    def call_format_handler(self, data):
        """calls a handler with self.handler_kwargs passed to the initializer"""
        format_handler = self.get_format_handler(data)
        handler_kwargs = self.get_handler_kwargs(format_handler)

        try:
            return format_handler(data.file, **handler_kwargs)
        except Exception as e:
            self.fail("format_handler", message=str(e))

    def get_handler_kwargs(self, handler_or_format) -> abc.Mapping:
        """get the kwargs that get passed to the handler"""
        return self.handler_kwargs.get(handler_or_format, {})

    def update_row(self, table_object, index, new_row):
        """update a specific row using table_object and index"""
        table_object[index] = new_row

    def process_table(self, table_object):
        """do some logic on the table before you receive it in parent's validated_data"""

        if self.row_validator:
            for i, row in table_object.iterrows():
                try:
                    new_row = self.row_validator(row, i, table_object)
                    if new_row is not None:
                        self.update_row(table_object, i, new_row)
                except serializers.ValidationError as e:
                    raise serializers.ValidationError(
                        {
                            "field_errors": e.detail,
                            "row": i,
                        }
                    )

        return table_object

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        table_object = self.call_format_handler(data)
        return self.process_table(table_object)

    def to_representation(self, value):
        raise serializers.ValidationError(
            "{} is a write_only field".format(self.__class__.__name__)
        )


class DebugSerializer(serializers.Serializer):
    def to_representation(self, serializer):
        if not isinstance(serializer, serializers.Serializer):
            raise serializers.ValidationError(
                "{} is not a valid serializer instance".format(serializer.__name__)
            )

        serializer.is_valid(raise_exception=True)
        parent = getattr(serializer, "parent", None)

        return {
            "class": serializer.__class__.__name__,
            "field_name": getattr(serializer, "field_name", None),
            "fields": serializer.get_fields(),
            "instance": getattr(serializer, "instance", None),
            "initial_data": serializer.initial_data,
            "parent": self.__class__(instance=parent.data) if parent else None,
            "default_error_messages": serializer.default_error_messages,
            "errors": serializer.errors,
            "data": serializer.data,
            "parameters": {
                "allow_null": serializer.allow_null,
                "validators": self.validators,
                "context": serializer.context,
                "label": serializer.label,
                "source": serializer.source,
                "many": isinstance(serializer, serializers.ListSerializer),
            },
        }


class Base64Field(serializers.CharField):
    """A field that accepts Base64 input.

    .. to_representation returns the string
    .. to_internal_value returns base64 string
    """

    default_error_messages = {
        **serializers.CharField.default_error_messages,
        "invalid_b64_string": "string provided is not valid base64",
    }

    def __init__(self, **kwargs):
        self.encoding = kwargs.pop("encoding", "utf-8")
        self.reverse = kwargs.pop("reverse", True)
        super().__init__(**kwargs)

    def to_base(self, s):
        """return the base64 encoded string"""
        return base64.b64encode(s.encode(self.encoding)).decode(self.encoding)

    def from_base(self, s, raise_exception=True):
        """return the string from the base64"""
        try:
            return base64.b64decode(s)
        except ValueError:
            if raise_exception:
                self.fail("invalid_b64_string")

    def to_representation(self, value: str):
        if self.reverse:
            return self.to_base(value)

        return self.from_base(value, raise_exception=False)

    def to_internal_value(self, data: str):
        data = super().to_internal_value(data)
        if self.reverse:
            return self.from_base(data)

        return self.to_base(data)


class EncryptedField(serializers.CharField):
    """to be implemented"""


class HashedField(serializers.CharField):
    """to be implemented"""


class ObfuscatedFieldMixin:
    obfuscator = Obfuscator

    def __init__(self, **kwargs):
        self.cutoff = kwargs.pop("cutoff", 4)
        self.from_end = kwargs.pop("from_end", True)
        self.char = kwargs.pop("char", "*")
        super().__init__(**kwargs)

    def to_representation(self, value):
        return self.obfuscator.obfuscate(
            value, cutoff=self.cutoff, from_end=self.from_end, char=self.char
        )


class ObfuscatedCharField(ObfuscatedFieldMixin, serializers.CharField):
    pass


class ObfuscatedEmailField(ObfuscatedFieldMixin, serializers.EmailField):
    def to_representation(self, value):
        return self.obfuscator.email(value)
