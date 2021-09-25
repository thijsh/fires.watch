import datetime


class Fires:
    @staticmethod
    def calculate(data):
        """
        Calculate portfolio value per month by:
        - Add savings = (income - expenses_per_year) / 12
        - Add portfolio percentage = yearly percentage back calculated to month
        - Subtract inflation percentage = yearly percentage back calculated to month
        - Increase inflation adjusted expenses per month
        - If 4% portfolio > expenses_per_year => pension start year / month

        Output to user:
        - Retirement age / duration in year
        - Inflation adjusted cost of living (i.e. 10k 50 years ago is > 100k now)
        - Graphs with portfolio, interest, and change per month and year
        """
        current_year = datetime.date.today().year
        portfolio = data["portfolio_value"]
        expenses_per_month = data["expenses_per_year"] / 12
        inflation_factor = (1 + data["inflation_percentage_per_year"] / 100) ** (1 / 12)
        portfolio_factor = (1 + data["portfolio_percentage_per_year"] / 100) ** (1 / 12)
        safe_rate_per_year = data["max_withdrawal_percentage_per_year"] / 100
        months = 0
        pension_started = False
        result = {
            "cost_of_living": None,
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
            savings_per_month = max(
                data["income_gross_per_year"] / 12 - expenses_per_month, 0
            )
            portfolio = portfolio * portfolio_factor + savings_per_month
            needed_portfolio = expenses_per_month * 12 / safe_rate_per_year
            if portfolio > needed_portfolio and pension_started is False:
                pension_started = True
                result["cost_of_living"] = round(expenses_per_month * 12)
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
            # Stop graph calculation after requested pension length
            if (
                pension_started
                and months >= result["months"] + 12 * data["years_duration"]
            ):
                break

        return result
