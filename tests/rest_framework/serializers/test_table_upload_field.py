import pandas as pd
import polars as pl
import pytest

from djkit.rest_framework.pandas import PandasTableUploadField
from djkit.rest_framework.polars import PolarsTableUploadField
from djkit.rest_framework.serializers import TableUploadField as BaseTableUploadField

POLARS_FIXTURES = ["csv_file", "xlsx_file", "json_file"]

PANDAS_FIXTURES = [
    "csv_file",
    "xlsx_file",
    "json_file",
    # "xml_file",
    # "sql_file",
]

ALL_DATA_FIXTURES = list(set(POLARS_FIXTURES) | set(PANDAS_FIXTURES))


def test_base_table_upload_field_is_write_only():
    assert (
        PandasTableUploadField().write_only is True
    ), "PandasTableUploadField is not write_only"
    assert (
        PolarsTableUploadField().write_only is True
    ), "PolarsTableUploadField is not write_only"


@pytest.mark.xfail
def test_reading_from_fields_should_fail():
    BaseTableUploadField().to_representation({})
    PandasTableUploadField().to_representation({})
    PolarsTableUploadField().to_representation({})


@pytest.mark.parametrize("file", ALL_DATA_FIXTURES, indirect=True)
@pytest.mark.xfail
def test_base_upload_field_read(file):
    BaseTableUploadField().to_internal_value(file)


@pytest.mark.parametrize("file", ALL_DATA_FIXTURES, indirect=True)
@pytest.mark.xfail
def test_base_table_upload_cant_be_used(file):
    BaseTableUploadField().to_internal_value(file)


@pytest.mark.parametrize("file", PANDAS_FIXTURES, indirect=True)
def test_allowed_formats_parsed_correctly_in_pandas(file):
    df = PandasTableUploadField().to_internal_value(file)
    assert isinstance(df, pd.DataFrame), "got {} instead of a dataframe".format(
        type(df).__name__
    )


@pytest.mark.parametrize("file", POLARS_FIXTURES, indirect=True)
def test_allowed_formats_parsed_correctly_in_polars(file, column_names):
    df = PolarsTableUploadField().to_internal_value(file)
    assert isinstance(df, pl.DataFrame), "got {} instead of a dataframe".format(
        type(df).__name__
    )


def test_format_handlers_are_all_callable_in_pandas():
    pandas_format_handlers = PandasTableUploadField().get_format_handlers()

    for pandas_format_handler in pandas_format_handlers.values():
        assert callable(
            pandas_format_handler
        ), "format_handler of type={} is not callable in {}".format(
            type(pandas_format_handler),
            PandasTableUploadField.__class__.__name__,
        )


def test_format_handlers_are_all_callable_in_polars():
    polars_format_handlers = PolarsTableUploadField().get_format_handlers()

    for polars_format_handler in polars_format_handlers.values():
        assert callable(
            polars_format_handler
        ), "format_handler of type={} is not callable in {}".format(
            type(polars_format_handler),
            PolarsTableUploadField.__class__.__name__,
        )


@pytest.mark.parametrize("file", ["json_file"], indirect=True)
def test_return_none_row_should_not_update_row_in_pandas(file, column_names):
    old_df: pd.DataFrame | None = None

    # set the old_df as the df in use, one time when it begnis
    def row_validator(row, i, df: pd.DataFrame):
        nonlocal old_df
        if i == 0:
            old_df = df

        return row

    df: pd.DataFrame = PandasTableUploadField(
        row_validator,
        handler_kwargs={
            "jso": {
                "convert_axes": True,
                "orient": "values",
            }
        },
    ).to_internal_value(file)

    assert df.equals(old_df), "DataFrame changed even when row_validator returned None"


def test_return_row_should_update_row(db):
    pass
