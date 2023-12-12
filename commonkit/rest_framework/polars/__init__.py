from ..serializers import TableUploadField as BaseTableUploadField

try:
    import polars as pl
except ImportError:
    pl = None

__all__ = ("TableUploadField", "PolarsTableUploadField")


class TableUploadField(BaseTableUploadField):
    handlers = {
        "csv": pl.read_csv,
        "json": pl.read_json,
        "xlsx": pl.read_excel,
        "xls": pl.read_excel,
        "xlsm": pl.read_excel,
        "xltm": pl.read_excel,
        "xltx": pl.read_excel,
        "xlsb": pl.read_excel,
        "odf": pl.read_excel,
        "ods": pl.read_excel,
        "odt": pl.read_excel,
    }


# Just in case you have a different TableUploadField
PolarsTableUploadField = TableUploadField
