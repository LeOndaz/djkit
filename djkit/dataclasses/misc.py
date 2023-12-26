import numbers
from dataclasses import dataclass


@dataclass
class Money:
    amount: numbers.Integral
    currency: str
