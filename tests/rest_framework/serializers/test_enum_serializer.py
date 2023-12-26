import pytest
from core.models import Human
from rest_framework import serializers

from djkit.rest_framework.serializers import EnumSerializer


@pytest.mark.xfail
def test_enum_serializer_fails_without_enum():
    EnumSerializer()  # noqa


@pytest.mark.xfail
def test_enum_serializer_with_another_param_type_than_enum():
    EnumSerializer(object)


def test_correct_representation_of_string_members():
    enum_serializer = EnumSerializer(Human.MilitaryStatus)
    assert enum_serializer.to_representation("exempted") == "exempted"
    assert enum_serializer.to_representation("postponed") == "postponed"
    assert enum_serializer.to_representation("served") == "served"


def test_correct_serialization_of_string_members():
    enum_serializer = EnumSerializer(Human.MilitaryStatus)

    assert enum_serializer.to_internal_value("EXEMPTED") == "exempted"
    assert enum_serializer.to_internal_value("POSTPONED") == "postponed"
    assert enum_serializer.to_internal_value("SERVED") == "served"


def test_to_internal_value_raises_error_on_unknown_string_member():
    enum_serializer = EnumSerializer(Human.MilitaryStatus)

    with pytest.raises(serializers.ValidationError):
        enum_serializer.to_internal_value("KICKED")


def test_to_internal_value_raises_error_on_unknown_int_member():
    enum_serializer = EnumSerializer(Human.Level)

    with pytest.raises(serializers.ValidationError):
        enum_serializer.to_internal_value("NEWBIE")


def test_correct_representation_of_int_members(
    exempted_human: Human, served_human: Human, postponed_human: Human
):
    enum_serializer = EnumSerializer(Human.Level)
    assert enum_serializer.to_representation(Human.Level.BEGINNER) == "BEGINNER"
    assert enum_serializer.to_representation(Human.Level.INTERMEDIATE) == "INTERMEDIATE"
    assert enum_serializer.to_representation(Human.Level.ADVANCED) == "ADVANCED"


def test_correct_serialization_of_int_members(
    exempted_human: Human, served_human: Human, postponed_human: Human
):
    enum_serializer = EnumSerializer(Human.Level)
    assert enum_serializer.to_internal_value("BEGINNER") == Human.Level.BEGINNER
    assert enum_serializer.to_internal_value("INTERMEDIATE") == Human.Level.INTERMEDIATE
    assert enum_serializer.to_internal_value("ADVANCED") == Human.Level.ADVANCED
