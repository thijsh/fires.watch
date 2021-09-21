import pytest
from django.urls.base import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def valid_payload():
    return {
        "birth_year": 1984,
        "years_duration": 30,
        "currency": "EUR",
        "income_gross_per_year": 50000,
        "expenses_per_year": 25000,
        "portfolio_value": 100000,
        "portfolio_percentage_per_year": 10,
        "inflation_percentage_per_year": 2,
    }


@pytest.fixture
def valid_payload_result():
    return {
        "portfolio": 785963,
        "months": 134,
        "age": 48,
    }


class TestFires:
    def test_calculate(self, admin_client, valid_payload, valid_payload_result):
        url = reverse("api:fires-calculate")
        response = admin_client.post(url, valid_payload)
        assert response.status_code == 200
        result = response.data["fires_calculate_result"]
        for variable in valid_payload:
            assert response.data[variable] == valid_payload[variable]
        for variable in valid_payload_result:
            assert result[variable] == valid_payload_result[variable]

    def test_calculate_graph(self, admin_client, valid_payload, valid_payload_result):
        url = reverse("api:fires-calculate")
        response = admin_client.post(url, valid_payload)
        assert response.status_code == 200
        result = response.data["fires_calculate_result"]
        expected_months = (
            valid_payload_result["months"] + valid_payload["years_duration"] * 12
        )
        assert len(result["graph_months"]) == expected_months  # 1200 max
        for month in result["graph_months"]:
            for variable in {"portfolio", "interest", "change"}:
                assert month[variable] != 0
        assert len(result["graph_years"]) == expected_months // 12  # 100 max
        for year in result["graph_years"]:
            for variable in {"portfolio", "interest", "change"}:
                assert year[variable] != 0

    @pytest.mark.parametrize(
        "variable,invalid_value",
        [
            ("birth_year", 0),
            ("years_duration", 0),
            ("currency", "aaaaa"),
            ("income_gross_per_year", -1),
            ("expenses_per_year", -1),
            ("portfolio_value", -1),
            ("portfolio_percentage_per_year", -101),
            ("inflation_percentage_per_year", -101),
        ],
    )
    def test_calculate_invalid_data(
        self, variable, invalid_value, admin_client, valid_payload
    ):
        url = reverse("api:fires-calculate")
        payload = valid_payload
        payload[variable] = invalid_value
        response = admin_client.post(url, payload)
        assert response.status_code == 400

    def test_calculation_timeout_no_result(self, admin_client):
        url = reverse("api:fires-calculate")
        payload = {
            "birth_year": 1984,
            "years_duration": 30,
            "currency": "EUR",
            "income_gross_per_year": 50000,
            "expenses_per_year": 50000,
            "portfolio_value": 1,
            "portfolio_percentage_per_year": 0,
            "inflation_percentage_per_year": 2,
        }
        response = admin_client.post(url, payload)
        assert response.status_code == 200
        result = response.data["fires_calculate_result"]
        for variable in ["portfolio", "age", "months"]:
            assert result[variable] is None
        assert len(result["graph_months"]) == 1200
        assert len(result["graph_years"]) == 100
