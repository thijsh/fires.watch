import pytest
from django.urls.base import reverse

pytestmark = pytest.mark.django_db


class TestFires:
    def test_calculate(self, admin_client):
        url = reverse("api:fires-calculate")
        payload = {
            "birth_year": 1984,
            "years_duration": 30,
            "currency": "EUR",
            "income_gross_per_year": 50000,
            "expenses_per_year": 25000,
            "portfolio_value": 100000,
            "portfolio_percentage_per_year": 10,
            "inflation_percentage_per_year": 2,
        }
        expected_response = payload | {
            "pension_months": 134,
        }
        response = admin_client.post(url, payload)
        assert response.status_code == 200
        for variable in expected_response:
            assert response.data[variable] == expected_response[variable]

    @pytest.mark.parametrize(
        "variable,invalid_value",
        [
            ("birth_year", 0),
            ("years_duration", 0),
            ("currency", "aaaaa"),
            ("income_gross_per_year", 0),
            ("expenses_per_year", 0),
            ("portfolio_value", 0),
            ("portfolio_percentage_per_year", 0),
            ("inflation_percentage_per_year", 0),
        ],
    )
    def test_calculate_invalid_data(self, variable, invalid_value, admin_client):
        url = reverse("api:fires-calculate")
        payload = {
            "birth_year": 0,
            "years_duration": 0,
            "currency": "EUR",
            "income_gross_per_year": 0,
            "expenses_per_year": 0,
            "portfolio_value": 0,
            "portfolio_percentage_per_year": -101,
            "inflation_percentage_per_year": -101,
        }
        payload[variable] = invalid_value
        response = admin_client.post(url, payload)
        assert response.status_code == 400
