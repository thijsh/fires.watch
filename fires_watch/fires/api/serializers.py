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
    Annual expenses_per_year (integer: >=0)
    Current portfolio value (integer: >=0)
    Expected portfolio ROR (float percentage: -100 through 100)
    Inflation (float percentage: -100 through 100)
        Default: average historical inflation for EUR/USD

    Output to user:
    - Retirement age / duration
    - Inflation adjusted result (i.e. 10k 50 years ago is 100k now)
    - Graphs per month and year
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
    fires_calculate_result = serializers.SerializerMethodField()

    def get_fires_calculate_result(self, inst):
        return self.calculate_fire(inst)

    def calculate_fire(self, data):
        """
        Calculate portfolio value per month by:
        - add savings = (income - expenses_per_year) / 12
        - add portfolio percentage = yearly percentage back calculated to month
        - subtract inflation percentage = yearly percentage back calculated to month
        If 4% / 12 of portfolio > expenses_per_year = pension start year / month
        """
        current_year = datetime.date.today().year
        portfolio = data["portfolio_value"]
        expenses_per_month = data["expenses_per_year"] / 12
        savings_per_month = data["income_gross_per_year"] / 12 - expenses_per_month
        inflation_factor = (1 + data["inflation_percentage_per_year"] / 100) ** (1 / 12)
        portfolio_factor = (1 + data["portfolio_percentage_per_year"] / 100) ** (1 / 12)
        safe_rate_per_year = 0.04
        months = 0
        pension_started = False
        result = {
            "portfolio": None,
            "months": None,
            "years": None,
            "age": None,
            "graph_months": [],
            "graph_years": [],
        }
        # Run calculation for a maximum of 100 years
        while months < 1200:
            # Start new year count the first month of the year
            if (months % 12) == 0:
                year = {
                    "portfolio": 0,
                    "interest": 0,
                    "change": 0,
                }
            months += 1
            expenses_per_month = expenses_per_month * inflation_factor
            interest = portfolio * (portfolio_factor - 1)
            portfolio = portfolio * portfolio_factor + savings_per_month
            needed_portfolio = expenses_per_month * 12 / safe_rate_per_year
            if portfolio > needed_portfolio and pension_started is False:
                pension_started = True
                result["portfolio"] = round(portfolio)
                result["months"] = months
                result["years"] = months // 12
                result["age"] = current_year - data["birth_year"] + months // 12
            # Store values per month for the graph
            month = {
                "portfolio": portfolio,
                "interest": interest,
                "change": (
                    -expenses_per_month if pension_started else savings_per_month
                ),
            }
            result["graph_months"].append(
                {
                    "portfolio": round(month["portfolio"]),
                    "interest": round(month["interest"]),
                    "change": round(month["change"]),
                }
            )
            # Add month values to year tally and store end of the year
            # NOTE: year portfolio is added and in next step divided by
            #       12 to get the average portfolio size during the year.
            for variable in month:
                year[variable] += month[variable]
            if (months % 12) == 0:
                result["graph_years"].append(
                    {
                        "year": months / 12,
                        "portfolio": year["portfolio"] // 12,
                        "interest": round(year["interest"]),
                        "change": round(year["change"]),
                    }
                )
            # Stop calculation after requested pension length
            if (
                pension_started
                and months >= result["months"] + 12 * data["years_duration"]
            ):
                break

        return result
