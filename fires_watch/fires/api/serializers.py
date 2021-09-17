import datetime

from rest_framework import serializers


class FiresCalculateSerializer(serializers.Serializer):
    """
    Serializer requires the following arguments:
    Year Of Birth (integer: 1900 - now)
    Duration in years of retirement (integer: 1 - 99)
        Default: Life expectancy → years/duration
    Currency (string: EUR/USD)
    Current annual net income (integer: >=0)
    Annual expenses (integer: >=0)
    Current portfolio value (integer: >=0)
    Expected portfolio ROR (float percentage: -100 through 100)
    Inflation (float percentage: -100 through 100)
        Default: average historical inflation for EUR/USD

    Output to user:
    Retirement age / duration
    Inflation adjusted result (i.e. 10k 50 years ago is 100k now)
        Rows for graph representation per month
    """

    # Required input
    birth_year = serializers.IntegerField(min_value=1900, max_value=2021)
    years_duration = serializers.IntegerField(min_value=1, max_value=99)
    currency = serializers.CharField(max_length=3)
    income_gross = serializers.IntegerField(min_value=1)
    expenses = serializers.IntegerField(min_value=1)
    portfolio_value = serializers.IntegerField(min_value=1)
    portfolio_percentage = serializers.FloatField(min_value=-100, max_value=100)
    inflation_percentage = serializers.FloatField(min_value=-100, max_value=100)

    # Calculated output
    pension_months = serializers.SerializerMethodField()

    def get_pension_months(self, inst):
        return self.calculate_fire(inst)

    def calculate_fire(self, data):
        """
        Calculate portfolio value per month by:
        - add savings = (income - expenses) / 12
        - add portfolio percentage = yearly percentage back calculated to month
        - subtract inflation percentage = yearly percentage back calculated to month
        If 4% / 12 of portfolio > expenses = pension start year / month
        """
        current_year = pension_year = datetime.date.today().year
        portfolio = data["portfolio_value"]
        expenses = data["expenses"]
        savings = data["income_gross"] - expenses
        inflation_factor = 1 + data["inflation_percentage"] / 100
        portfolio_factor = 1 + data["portfolio_percentage"] / 100
        safe_rate = 0.04
        while True:
            expenses = expenses * inflation_factor
            portfolio = portfolio * portfolio_factor + savings
            needed_portfolio = expenses / safe_rate
            pension_year += 1
            if portfolio > needed_portfolio:
                return (pension_year - current_year) * 12
