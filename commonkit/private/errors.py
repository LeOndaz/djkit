"""
all errors are implemented as functions, this may change in the future
that's why the file name is prefixed with _, private files are subject to interface change
"""


def serializer_cant_pass_ready_only(serializer):
    return "can't pass read_only to a write_only serializer {}".format(
        serializer.__class__.__name__,
    )


def serializer_write_only_by_default(serializer):
    return "serializer {} is already write_only by default".format(
        serializer.__class__.__name__,
    )


def handler_kwargs_must_be_mapping(handler, obj):
    return "{}.handler_kwargs must be an instance of `abc.Mapping`, got `{}`".format(
        handler.__class__.__name__,
        obj,
    )


def handlers_and_handler_mutually_exclusive():
    return (
        "attrs `handler` and `handlers` are mutually exclusive, please only provide one"
    )


def must_pass_row_when_key_is_row():
    return "must pass row in kwargs when key=row"


def must_pass_message_when_key_is_row():
    return "must pass a message for errors in rows"


def serializer_cant_be_used_independently(serializer):
    return "{} can't be used as a dependant serializer".format(
        serializer.__class__.__name__,
    )


def table_upload_handler_must_be_a_callable(field):
    return (
        "{}.handler must be a callable which accepts row, index & table_object".format(
            field.__class__.__name__,
        )
    )


def table_upload_handlers_must_be_mapping(field, got):
    return "{}.handlers must be of type collections.Mapping, got {}".format(
        field.__class__.__name__,
        got.__class__.__name__,
    )


def table_upload_no_format_handlers_found():
    return (
        "must add some format_handlers using your favourite library like"
        " pola.rs or pandas or you can implement your custom handler for it."
    )


def must_provide_serializer_instance(got):
    return "must provide serializer instance, got {}".format(got)


def must_pass_enum_to_enum_serializer(got):
    return "must pass enum to EnumSerializer, got {}".format(got)
