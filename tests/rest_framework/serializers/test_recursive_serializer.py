from core.serializers import CategorySerializer


def test_recursive_serializer_many(db, subcategories):
    serializer = CategorySerializer(subcategories, many=True)

    for category_data, subcategory in zip(serializer.data, subcategories):
        assert category_data["name"] == subcategory.name
        assert category_data["parent"]["id"] == subcategory.parent.id


def test_recursive_serializer_single(db, subcategories):
    subcategory = subcategories.first()
    serializer = CategorySerializer(subcategory)
    assert serializer.data["name"] == subcategory.name
    assert serializer.data["parent"]["id"] == subcategory.parent.id
