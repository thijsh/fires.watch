import datetime


class Fires:
    @staticmethod
    def calculate(data):
        """
        Calculate portfolio value per month by:
        - Adding savings ((income - expenses_per_year) / 12)
        - Adding monthly portfolio percentage (deduced from yearly percentage)
        - Determine monthly inflation percentage (deduced from yearly percentage)
        - Subtracting monthly inflation adjusted expenses

        Determine retirement age based on:
        - Portfolio growth, expenses, and 'safe' withdrawal rate

        Returned retirement age details, at the exact moment of retirement:
        - Cost of Living
        - Portfolio Value
        - Months from now (to moment of retirement)
        - Years from now (to moment of retirement)
        - Age (when retiring)

        Returned datasets meant for graphing:
        - Monthly
        - Yearly

        For each datapoint in each dataset, we return:
        - Total portfolio value
        - Total interest value
        - Total change (result of expenses, savings, withdrawal rate)
        """

        current_year = datetime.date.today().year

        # Extract user input from data and deduce the values we'll need
        portfolio = data["portfolio_value"]
        expenses_per_month = data["expenses_per_year"] / 12
        inflation_factor = (1 + data["inflation_percentage_per_year"] / 100) ** (1 / 12)
        portfolio_factor = (1 + data["portfolio_percentage_per_year"] / 100) ** (1 / 12)
        safe_rate_per_year = data["max_withdrawal_percentage_per_year"] / 100

        # Initialize some values to start our monthly calculation loop
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

        # Run a monthly calculation, for a maximum of 100 years
        while months < 1200:
            # At the start of every year ..
            if (months % 12) == 0:
                # .. start counters for this year ..
                year = {
                    "portfolio": 0,
                    "interest": 0,
                    "change": 0,
                }
            months += 1

            # Calculate values for this month
            expenses_per_month = expenses_per_month * inflation_factor
            interest = portfolio * (portfolio_factor - 1)
            savings_per_month = max(
                data["income_gross_per_year"] / 12 - expenses_per_month, 0
            )

            # Calculate portfolio values from this month's data
            portfolio = portfolio * portfolio_factor + savings_per_month
            needed_portfolio = expenses_per_month * 12 / safe_rate_per_year

            # Determine if the target portfolio has been reached this moonth ..
            if portfolio > needed_portfolio and pension_started is False:

                # .. if so, retirement starts this month :)
                pension_started = True  # Run this code block only once

                # Remember these values from this first retirement month
                result["cost_of_living"] = round(expenses_per_month * 12)
                result["portfolio"] = round(portfolio)
                result["months"] = months  # Months until retirement
                result["years"] = months // 12  # Truncate float to integer
                result["age"] = current_year - data["birth_year"] + months // 12
            # Store this month's value as graph data
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
