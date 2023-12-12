# drf-common


## Installation

- `pip install commonkit`

### Examples

```python
# models.py
from django.db import models


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
```

```python
# serializers.py
from rest_framework import serializers
from commonkit.rest_framework.serializers import EnumSerializer
from example.core import models


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
```

## Example serialization

```python
# wherever.py
from example.core.serializers import HumanSerializer
from example.core.models import Human

human = Human.objects.find(id=1)
serializer = HumanSerializer(human)  # level = BEGINNER, military_status = EXEMPTED
```

## Example deserialization

```python
# wherever.py
from example.core.serializers import HumanSerializer

data = {
    "level": "BEGINNER",
    "MILITARY_STATUS": "EXEMPTED",
}

instance = HumanSerializer(data=data)
instance.is_valid()
instance.save()
```


To run the project

- `pip install -r requirements.txt`
- `pre-commit install`

To build the docs

- `make html`

To run the tests

- `pytest .`
