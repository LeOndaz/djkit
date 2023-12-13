from functools import total_ordering

from django.core import validators
from django.db.models import Field


@total_ordering
class NonDatabaseFieldBase:
    """Base class for all fields that are not stored in the database."""

    empty_values = list(validators.EMPTY_VALUES)

    # Field flags
    auto_created = False
    blank = True
    concrete = False
    editable = False
    unique = False

    is_relation = False
    remote_field = None

    many_to_many = None
    many_to_one = None
    one_to_many = None
    one_to_one = None

    def __init__(self):
        self.column = None
        self.primary_key = False
        self.attname = ""
        self.name = ""
        self.model = None

        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def __eq__(self, other):
        if isinstance(other, (Field, NonDatabaseFieldBase)):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (Field, NonDatabaseFieldBase)):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def __hash__(self):
        return hash(self.creation_counter)

    def contribute_to_class(self, cls, name, **kwargs):
        self.attname = self.name = name
        self.model = cls
        cls._meta.add_field(self, private=True)
        setattr(cls, name, self)

    def clean(self, value, model_instance):
        return value


class MonetaryField(NonDatabaseFieldBase):
    pass
