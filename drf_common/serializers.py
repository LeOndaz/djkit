from rest_framework import serializers


class RecursiveSerializer(serializers.Serializer):
    """
    A serializer that can be used to recursively serialize an object.

    example usage:

    class Human(serializers.Serializer):
        name = serializers.CharField()
        children = RecursiveSerializer(many=True)
        father = RecursiveSerializer()
        mother = RecursiveSerializer()

    """

    def to_representation(self, value):
        if isinstance(self.parent, serializers.ListSerializer):
            return self.parent.parent.__class__(value).data

        return self.parent.__class__(value).data
