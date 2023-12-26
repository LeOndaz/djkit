import decimal
import numbers
from functools import total_ordering

from django.core import exceptions, validators
from django.db.models import Field

from djkit.dataclasses.misc import Money


@total_ordering
class NonDatabaseField(Field):
    """A field that's not stored in databases"""

    empty_values = validators.EMPTY_VALUES

    auto_created = False
    blank = True
    concrete = False
    editable = False
    unique = False

    is_relation = False
    remote_field = None

    one_to_one = None
    one_to_many = None
    many_to_one = None
    many_to_many = None

    prevent_kwargs = ["primary_key", "blank", "editable", "unique"]

    def __init__(self, *args, **kwargs):
        for kwarg_name in self.prevent_kwargs:
            passed_kwargs = []

            if kwargs.get(kwarg_name, None):
                passed_kwargs.append(kwarg_name)

            if passed_kwargs:
                raise exceptions.ValidationError(
                    "parameters [%s] not allowed in %s"
                    % (
                        ", ".join(passed_kwargs),
                        self.__class__.__name__,
                    )
                )

        super().__init__(*args, **kwargs, primary_key=False)

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, private_only=True)

    def clean(self, value, model_instance):
        return value


class MoneyField(NonDatabaseField):
    description = "A field that represents an amount of money and the currency used"

    def __init__(
        self,
        amount_field="price_amount",
        currency_field="price_currency",
        verbose_name=None,
    ):
        super(MoneyField, self).__init__(verbose_name=verbose_name)
        self.amount_field = amount_field
        self.currency_field = currency_field

    def __str__(self):
        return "%s(amount_field=%s, currency_field=%s)" % (
            self.__class__.__name__,
            self.amount_field,
            self.currency_field,
        )

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        amount = getattr(instance, self.amount_field)
        currency = getattr(instance, self.currency_field)
        if amount is not None and currency is not None:
            return Money(amount, currency)
        return self.get_default()

    def __set__(self, instance, value: Money | numbers.Number):
        default = self.get_default()
        currency = default.currency if default else None

        if isinstance(value, Money):
            amount = decimal.Decimal(value.amount)
        else:
            amount = value

        # update instance
        setattr(instance, self.amount_field, amount)
        setattr(instance, self.currency_field, currency)

    def get_default(self):
        default_currency = self.model._meta.get_field(self.currency_field).get_default()
        default_amount = self.model._meta.get_field(self.amount_field).get_default()

        if default_amount is None:
            return None

        return Money(default_amount, default_currency)
