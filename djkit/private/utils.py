import inspect
from functools import wraps

from .loggers import logger


def subject_to_change(obj):
    warning_message = "{} is subject to interface change, use with caution".format(
        obj.__name__
    )
    setattr(obj, "_subject_to_change", True)

    if inspect.isclass(obj):
        old_init = obj.__init__

        @wraps(old_init)
        def new_init(self, *args, **kwargs):
            logger.warn(warning_message)
            old_init(self, *args, **kwargs)

        obj.__init__ = new_init
        return obj

    elif inspect.isfunction(obj):

        @wraps(obj)
        def new_func(*args, **kwargs):
            logger.warn(warning_message)
            return obj(*args, **kwargs)

        return new_func


def validate_row_with_serializer(serializer_class, context=None):
    if context is None:
        context = {}

    def validator(row, i, table):
        nonlocal serializer_class

        serializer = serializer_class(
            data=row.to_dict(),
            context={
                **context,
                "row": row,
                "index": i,
                "table_object": table,
            },
        )

        serializer.is_valid(raise_exception=True)
        return serializer.save()

    return validator
