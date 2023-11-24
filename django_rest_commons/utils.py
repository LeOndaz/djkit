def validate_row_with_serializer(serializer_class, context=None):
    if context is None:
        context = {}

    def validator(row, i, table):
        nonlocal serializer_class

        serializer = serializer_class(
            data=row.to_dict(),
            context={
                **context,
                "row": row,
                "index": i,
                "table_object": table,
            },
        )

        serializer.is_valid(raise_exception=True)
        return serializer.save()

    return validator
