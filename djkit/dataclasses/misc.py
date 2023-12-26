import decimal
from dataclasses import dataclass


@dataclass
class Money:
    amount: decimal.Decimal
    currency: str
