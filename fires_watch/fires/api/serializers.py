from rest_framework import serializers

from fires_watch.fires.fires import Fires


class FiresCalculateSerializer(serializers.Serializer):
    """
    Serializer requires the following arguments:
    - Year Of Birth (integer: 1900 - now)
    - Duration in years of retirement (integer: 1 - 99)
        TODO: Default: Life expectancy → years/duration
    - Currency (string: EUR/USD)
    - Current annual net income (integer: >=0)
    - Annual expenses_per_year (integer: >=0)
    - Current portfolio value (integer: >=0)
    - Expected portfolio ROR (float percentage: -100 through 100)
    - Inflation (float percentage: -100 through 100)
        TODO: Default: average historical inflation for EUR/USD
    """

    # Required input (all values per year)
    birth_year = serializers.IntegerField(min_value=1900, max_value=2021)
    years_duration = serializers.IntegerField(min_value=1, max_value=99, default=30)
    currency = serializers.CharField(max_length=3, default="EUR")
    income_gross_per_year = serializers.IntegerField(min_value=1)
    expenses_per_year = serializers.IntegerField(min_value=1)
    portfolio_value = serializers.IntegerField(min_value=1)
    portfolio_percentage_per_year = serializers.FloatField(
        min_value=-100, max_value=100, default=10
    )
    inflation_percentage_per_year = serializers.FloatField(
        min_value=-100, max_value=100, default=2
    )
    max_withdrawal_percentage_per_year = serializers.FloatField(
        min_value=1, max_value=10, default=4
    )

    # Calculated output
    fires_calculate_result = serializers.SerializerMethodField()

    def get_fires_calculate_result(self, inst):
        return Fires.calculate(inst)
