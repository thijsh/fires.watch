import datetime


class UserInfo:
    birth_year: int
    current_portfolio: int
    income_yearly: int
    income_monthly: int
    expenses_monthly: int
    savings_monthly: int
    inflation_percent_monthly: float
    portfolio_interest_percent_monthly: float
    safe_rate_yearly: float

    def __init__(self, data):
        self.birth_year = data["birth_year"]
        self.current_portfolio = data["portfolio_value"]
        self.income_yearly = data["income_gross_per_year"]
        self.income_monthly = self.income_yearly / 12
        self.expenses_monthly = data["expenses_per_year"] / 12
        self.savings_monthly = max(self.income_monthly - self.expenses_monthly, 0)
        self.inflation_percent_monthly = (
            1 + data["inflation_percentage_per_year"] / 100
        ) ** (1 / 12)
        self.portfolio_interest_percent_monthly = (
            1 + data["portfolio_percentage_per_year"] / 100
        ) ** (1 / 12)
        self.safe_rate_yearly = data["max_withdrawal_percentage_per_year"] / 100


class MonthlyResults:
    userinfo: UserInfo
    interest: int
    savings: int
    target_portfolio: int

    def __init__(self, userinfo):
        self.userinfo = userinfo

    def transactions(self):
        # Calculate values for this month
        self.userinfo.expenses_monthly *= self.userinfo.inflation_percent_monthly
        self.interest = self.userinfo.current_portfolio * (
            self.userinfo.portfolio_interest_percent_monthly - 1
        )
        self.savings = max(
            self.userinfo.income_monthly - self.userinfo.expenses_monthly, 0
        )

    def portfolio_values(self):
        # Calculate portfolio values from this month's data
        self.userinfo.current_portfolio = (
            self.userinfo.current_portfolio
            * self.userinfo.portfolio_interest_percent_monthly
            + self.savings
        )
        self.target_portfolio = (
            self.userinfo.expenses_monthly * 12 / self.userinfo.safe_rate_yearly
        )


class Retirement:
    userinfo: UserInfo
    pension_started: bool
    current_year: int
    cost_of_living: int
    portfolio: int
    months: int
    years: int
    age: int

    def __init__(self, userinfo):
        self.userinfo = userinfo
        self.pension_started = False

    def goal_reached(self, target_portfolio):
        """Determine if the target portfolio has been reached this month."""

        if (
            self.userinfo.current_portfolio > target_portfolio
            and not self.pension_started
        ):
            return True

        return False

    def calculate_result(self, months):
        """
        Determines retirement age details.
        Should only run once, if self.goal_reached returns True.
        """

        self.pension_started = True

        self.current_year = datetime.date.today().year

        # Remember these values from this first retirement month
        self.cost_of_living = round(self.userinfo.expenses_monthly * 12)
        self.portfolio = round(self.userinfo.current_portfolio)
        self.months = months  # Months until retirement
        self.years = self.months // 12  # Truncate float to integer
        self.age = self.current_year - self.userinfo.birth_year + self.months // 12


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

        # Extract userinfo input from data and parse the values we'll need
        userinfo = UserInfo(data)

        # Initialize monthly calculators
        monthly = MonthlyResults(userinfo)

        # Initialize retirement calculator
        retirement = Retirement(userinfo)

        # Initialize some values to start our monthly calculation loop
        months = 0
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
            monthly.transactions()
            monthly.portfolio_values()

            if retirement.goal_reached(monthly.target_portfolio):

                # Remember these values from this first retirement month
                retirement.calculate_result(months)
                result["cost_of_living"] = retirement.cost_of_living
                result["portfolio"] = retirement.portfolio
                result["months"] = retirement.months  # Months until retirement
                result["years"] = retirement.years  # Truncate float to integer
                result["age"] = retirement.age

            # Store this month's value as graph data
            month = {
                "portfolio": userinfo.current_portfolio,
                "interest": monthly.interest,
                "change": (
                    -userinfo.expenses_monthly
                    if retirement.pension_started
                    else monthly.savings
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
                retirement.pension_started
                and months >= result["months"] + 12 * data["years_duration"]
            ):
                break

        return result
