import pytest
from django.shortcuts import reverse


@pytest.mark.parametrize("api", ["improved_json_renderer"], indirect=True)
def test_correct_response_on_field_errors(api):
    path = reverse("improved-json-renderer")
    response = api.post(path, data={})

    data = response.json()

    assert data["field_errors"]["level"]
    assert data["field_errors"]["military_status"]
    assert data["non_field_errors"] == []


@pytest.mark.parametrize("api", ["improved_json_renderer"], indirect=True)
def test_correct_response_on_non_field_errors(api):
    path = reverse("improved-json-renderer")
    response = api.get(path, data={"fail": True})
    data = response.json()

    assert data["non_field_errors"] == ["INTENTIONAL_FIELD_ERROR"]
    assert data["field_errors"] == {}


@pytest.mark.parametrize("api", ["improved_json_renderer"], indirect=True)
def test_correct_response_on_request_success(api):
    path = reverse("improved-json-renderer")
    response = api.get(path, data={"fail": False})
    data = response.json()
    assert data["key"] == "value"
