import pytest
from django.urls import resolve, reverse

pytestmark = pytest.mark.django_db


def test_calculate():
    assert reverse("api:fires-calculate") == "/api/fires/calculate/"
    assert resolve("/api/fires/calculate/").view_name == "api:fires-calculate"
