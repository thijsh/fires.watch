# import datetime

from rest_framework import serializers


class FiresCalculateSerializer(serializers.Serializer):
    """
    Serializer requires the following arguments:
    Year Of Birth (integer: 1900 - now)
    Duration in years of retirement (integer: 1 - 99)
        Default: Life expectancy → years/duration
    Currency (string: EUR/USD)
    Current annual net income (integer: >=0)
    Annual expenses_per_year (integer: >=0)
    Current portfolio value (integer: >=0)
    Expected portfolio ROR (float percentage: -100 through 100)
    Inflation (float percentage: -100 through 100)
        Default: average historical inflation for EUR/USD

    Output to user:
    Retirement age / duration
    Inflation adjusted result (i.e. 10k 50 years ago is 100k now)
        Rows for graph representation per month
    """

    # Required input (all values per year)
    birth_year = serializers.IntegerField(min_value=1900, max_value=2021)
    years_duration = serializers.IntegerField(min_value=1, max_value=99)
    currency = serializers.CharField(max_length=3)
    income_gross_per_year = serializers.IntegerField(min_value=1)
    expenses_per_year = serializers.IntegerField(min_value=1)
    portfolio_value = serializers.IntegerField(min_value=1)
    portfolio_percentage_per_year = serializers.FloatField(
        min_value=-100, max_value=100
    )
    inflation_percentage_per_year = serializers.FloatField(
        min_value=-100, max_value=100
    )

    # Calculated output
    pension_months = serializers.SerializerMethodField()

    def get_pension_months(self, inst):
        return self.calculate_fire(inst)

    def calculate_fire(self, data):
        """
        Calculate portfolio value per month by:
        - add savings = (income - expenses_per_year) / 12
        - add portfolio percentage = yearly percentage back calculated to month
        - subtract inflation percentage = yearly percentage back calculated to month
        If 4% / 12 of portfolio > expenses_per_year = pension start year / month
        """
        # current_year = datetime.date.today().year
        portfolio = data["portfolio_value"]
        expenses_per_month = data["expenses_per_year"] / 12
        savings_per_month = data["income_gross_per_year"] / 12 - expenses_per_month
        inflation_factor = (1 + data["inflation_percentage_per_year"] / 100) ** (1 / 12)
        portfolio_factor = (1 + data["portfolio_percentage_per_year"] / 100) ** (1 / 12)
        safe_rate_per_year = 0.04
        months = 0
        while True:
            expenses_per_month = expenses_per_month * inflation_factor
            portfolio = portfolio * portfolio_factor + savings_per_month
            needed_portfolio = expenses_per_month * 12 / safe_rate_per_year
            months += 1
            if portfolio > needed_portfolio:
                return months
