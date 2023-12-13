# CommonKit

## Installation

- `pip install commonkit`

## Examples

#### Obfuscation

```python
from commonkit.utils import Obfuscator

Obfuscator.email("abcdqweqwe@test.com") # abcdq****@test.com'
Obfuscator.obfuscate('my_super_confidential_secret')  # 'my_super_confidential_s*****'

```


#### Django rest framework related examples
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

#### Example serialization

```python
# wherever.py
from example.core.serializers import HumanSerializer
from example.core.models import Human

human = Human.objects.find(id=1)
serializer = HumanSerializer(human)  # level = BEGINNER, military_status = EXEMPTED
```

#### Example deserialization

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

#### Got some endpoints that accept files in table formats? got you

1. Assuming Pandas

```python
import pandas as pd
from commonkit.rest_framework.pandas import TableUploadField  # or PandasTableUploadField
from rest_framework import serializers


class MySerializer(serializers.ModelSerializer):
    file = TableUploadField()

    def create(self, validated_data):
        file: pd.DataFrame = validated_data['file']
        # do logic, don't do row based validation here
        return validated_data

    # optional method
    def validate_file_row(self, row, index, table_df):
        if row.iloc[0] == "X":
            row.iloc[0] = "Y"

        # return new row, or None and changes won't be reflected
        return row
```

2. Assuming Pola.rs

```python
import polars as pl
from commonkit.rest_framework.polars import TableUploadField  # or PolarsTableUploadField
from rest_framework import serializers


class MySerializer(serializers.ModelSerializer):
    file = TableUploadField()

    def create(self, validated_data):
        file: pl.DataFrame = validated_data['file']
        # do logic, don't do row based validation here
        return validated_data

    # optional method
    def validate_file_row(self, row, index, table_df):
        # do polars logic, return new row or None
        return row
```

- `TableUploadField` is `write_only`
- TableUploadField is easily extended, use your own library if you want

```python
from commonkit.rest_framework.serializers import TableUploadField as BaseTableUploadField


def read_csv(source):
    return ...


def read_excel(source):
    return ...


class TableUploadField(BaseTableUploadField):
    handlers = {
        "csv": read_csv,
        "xlsx": read_excel,
        "xls": read_excel,
        "xlsm": read_excel,
        "xlsb": read_excel,
        "odf": read_excel,
        "ods": read_excel,
        "odt": read_excel,
    }

    def update_row(self, table_object: "YourLibraryDataFrame", index, new_row):
        """how your library updates the row"""


```

#### Supported formats are the keys in handlers

```python
can_parse_csv = "csv" in field.allowed_upload_formats
```

#### Or
```python
can_parse_csv = field.is_allowed_format('obj') # False
```

#### Custom kwargs for handlers in TableFieldUpload

```python
from commonkit.rest_framework.pandas import PandasTableUploadField
import pandas as pd

class Serializer(...):
    pandas_file = PandasTableUploadField(handler_kwargs={
        # by format
        "xlsx": {
            # args for read_excel would be here
            "engine": "openpyxl"
        },
        # or by reference
        pd.read_csv: {
            "delimiter": "\t"
        }
    })
```

- The same logic applies to all `TableUploadField` subclasses.

- commonkit provides easily methods for overriding most of the logic.
- If you want a field that does aggregation or something, override `process_table` on `TableUploadField`


#### Obfuscation

```python
from commonkit.rest_framework.serializers import ObfuscatedCharField, ObfuscatedEmailField, ObfuscatedFieldMixin


class MySerializer(...):
    email = ObfuscatedEmailField()  # in the API, it's obfuscated
    name = ObfuscatedCharField()  # same applies here


class MyCustomObfuscatedApiKeyField(ObfuscatedFieldMixin, MyApiKeyField):
    pass

```


#### Better error handling
```python

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "commonkit.rest_framework.renderers.JSONRenderer"
    ]
}
```

This will change you response schema in case of errors to

```python
response = {
    "field_errors": [],
    "non_field_errors": []
}
```

## Contributions

To run the project locally

- `pip install poetry`
- `poetry install`
- `poetry shell`
- `pre-commit install`

To build the docs

- `make html`

To run the tests

- `pytest .`
