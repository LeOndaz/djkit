"""
Using a mix between polars and pandas, polars for performance and pandas for features
that are not in polars
"""

import io
import mimetypes

import pandas as pd
import polars as pl
import pytest
from core.models import Category, Human
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from rest_framework.test import APIClient

from djkit.rest_framework.renderers import JSONRenderer

mimetypes.init()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    faker = Faker()

    with django_db_blocker.unblock():
        Human.objects.bulk_create(
            [
                Human(
                    name=faker.name(),
                    level=i
                    if i <= 2
                    else i % 3,  # remainder of dividing by 3 can be 0, 1, 2
                    military_status=Human.MilitaryStatus.values[i if i <= 2 else i % 3],
                    email=faker.email(),
                )
                for i in range(10)
            ]
        )

        parents = Category.objects.bulk_create(
            [Category(name=faker.bs(), parent=None) for _ in range(5)]
        )

        for parent in parents:
            Category.objects.bulk_create(
                [
                    Category(
                        name=faker.bs(),
                        parent=parent,
                    )
                    for _ in range(5)
                ]
            )


@pytest.fixture
def humans(db):
    return Human.objects.all()


@pytest.fixture
def exempted_human(humans):
    return humans.filter(military_status=Human.MilitaryStatus.EXEMPTED).first()


@pytest.fixture
def served_human(humans):
    return humans.filter(military_status=Human.MilitaryStatus.SERVED).first()


@pytest.fixture
def postponed_human(humans):
    return humans.filter(military_status=Human.MilitaryStatus.POSTPONED).first()


@pytest.fixture
def column_names():
    return ["name", "address", "job", "company", "phone_number"]


@pytest.fixture
def file_data(faker):
    from faker.providers import address, company, job, phone_number

    for provider in [address, company, phone_number, job]:
        faker.add_provider(provider)

    return [
        [faker.name(), faker.address(), faker.job(), faker.bs(), faker.phone_number()]
        for _ in range(10)
    ]


@pytest.fixture
def csv_file(file_data, column_names):
    buffer = io.BytesIO()
    pl.DataFrame(file_data, schema=column_names).write_csv(buffer, include_header=True)
    buffer.seek(0)
    return SimpleUploadedFile(
        "csv_file.csv", buffer.read(), mimetypes.types_map[".csv"]
    )


@pytest.fixture
def xlsx_file(file_data, column_names):
    buffer = io.BytesIO()
    pl.DataFrame(file_data, schema=column_names).write_excel(buffer)
    buffer.seek(0)
    return SimpleUploadedFile(
        "xlsx_file.xlsx", buffer.read(), mimetypes.types_map[".xls"]
    )


@pytest.fixture
def json_file(file_data, column_names):
    buffer = io.BytesIO()
    pl.DataFrame(file_data, schema=column_names).write_json(buffer)
    buffer.seek(0)
    return SimpleUploadedFile(
        "json_file.json", buffer.read(), mimetypes.types_map[".json"]
    )


@pytest.fixture
def xml_file(file_data, column_names):
    buffer = io.BytesIO()
    pd.DataFrame(file_data, columns=column_names).to_xml(buffer)
    buffer.seek(0)
    return SimpleUploadedFile(
        "xml_file.xml", buffer.read(), mimetypes.types_map[".xml"]
    )


# @pytest.fixture
# def sql_file(data):
#     buffer = io.BytesIO()
#     pd.DataFrame(data).to_sql("sql_file.sql", buffer) # TODO needs con parameter
#     buffer.seek(0)
#     return SimpleUploadedFile("sql_file.sql", buffer.read(), "application/sql")
#


@pytest.fixture
def file(request):
    fixture_name = request.param
    return request.getfixturevalue(fixture_name)


@pytest.fixture
def human(request):
    fixture_name = request.param
    return request.getfixturevalue(fixture_name)


@pytest.fixture
def categories():
    return Category.objects.filter(parent__isnull=True)


@pytest.fixture
def subcategories():
    return Category.objects.filter(parent__isnull=False)


@pytest.fixture
def api(request):
    if getattr(request, "param", None) == "improved_json_renderer":

        class NewApiClient(APIClient):
            default_format = "json"
            renderer_classes_list = [JSONRenderer]

        return NewApiClient()

    return APIClient()
