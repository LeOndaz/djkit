from ..serializers import TableUploadField as BaseTableUploadField

try:
    import pandas as pd
except ImportError:
    pd = None

__all__ = ("TableUploadField", "PandasTableUploadField")


class TableUploadField(BaseTableUploadField):
    handlers = {
        "csv": pd.read_csv,
        "xlsx": pd.read_excel,
        "xls": pd.read_excel,
        "xlsm": pd.read_excel,
        "xlsb": pd.read_excel,
        "odf": pd.read_excel,
        "ods": pd.read_excel,
        "odt": pd.read_excel,
        "sql": pd.read_sql,
        "json": pd.read_json,
        "xml": pd.read_xml,
    }

    def update_row(self, table_object, index, new_row):
        table_object.iloc[index] = new_row


PandasTableUploadField = TableUploadField
