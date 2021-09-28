import datetime
from dataclasses import asdict, dataclass
from typing import List


@dataclass
class Result:
    """
    Contains all calculated results.
    Dataclass, so it can be converted into a dictionary for serializing.

    At the moment retirement is reached, the following variables are recorded:
    - cost_of_living
    - portfolio
    - months
    - years
    - age

    """

    cost_of_living: int
    portfolio: int
    months: int
    years: int
    age: int
    pension_started: bool
    graph_months: List
    graph_years: List

    def __init__(self):
        self.cost_of_living = None
        self.portfolio = None
        self.months = None
        self.years = None
        self.age = None
        self.pension_started = False
        self.graph_months = []
        self.graph_years = []


class UserInfo:
    """Contains all initial user info, and the Result() class."""

    birth_year: int
    years_duration: int
    current_portfolio: int
    initial_portfolio: int
    income_yearly: int
    income_monthly: int
    expenses_monthly: int
    savings_monthly: int
    inflation_percent_monthly: float
    portfolio_interest_percent_monthly: float
    safe_rate_yearly: float
    current_year: int
    result: Result

    def __init__(self, data):
        """Parse user input and determine initial values."""

        # Parse user input
        self.birth_year = data["birth_year"]
        self.years_duration = data["years_duration"]
        self.initial_portfolio = data["portfolio_value"]
        self.current_portfolio = self.initial_portfolio
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
        self.current_year = datetime.date.today().year

        # Initialize Result class
        self.result = Result()


class YearlyResults:
    """Calculates and tracks yearly results."""

    data: object

    def start_year(self):
        """Set yearly values to zero at the start of the year."""
        self.data = {
            "portfolio": 0,
            "interest": 0,
            "change": 0,
        }

    def save(self, months):
        """Save the yearly totals for further processing."""
        self.data = {
            "year": months / 12,
            "portfolio": self.data["portfolio"] // 12,
            "interest": round(self.data["interest"]),
            "change": round(self.data["change"]),
        }


class MonthCalculator:
    """Calculates and tracks monthly results."""

    userinfo: UserInfo
    yearly: YearlyResults
    count: int
    interest: int
    savings: int
    target_portfolio: int
    data: object

    def __init__(self, userinfo):
        """Set initial values"""
        self.userinfo = userinfo
        self.count = 0
        self.yearly = YearlyResults()

    def transactions(self):
        """
        Calculate monthly transaction values:
        - Expenses
        - Interest
        - Savings
        """
        self.userinfo.expenses_monthly *= self.userinfo.inflation_percent_monthly
        self.interest = self.userinfo.current_portfolio * (
            self.userinfo.portfolio_interest_percent_monthly - 1
        )
        self.savings = max(
            self.userinfo.income_monthly - self.userinfo.expenses_monthly, 0
        )

    def portfolio_values(self):
        """
        Calculate this month's portfolio values:
        - Current portfolio value (based on interest and savings)
        - Target portfolio (based on 'safe' withdrawal rate)
        """
        self.userinfo.current_portfolio = (
            self.userinfo.current_portfolio
            * self.userinfo.portfolio_interest_percent_monthly
            + self.savings
        )
        self.target_portfolio = (
            self.userinfo.expenses_monthly * 12 / self.userinfo.safe_rate_yearly
        )

    def save(self):
        """Store monthly results for further processing."""
        self.data = {
            "portfolio": round(self.userinfo.current_portfolio),
            "interest": round(self.interest),
            "change": round(
                -self.userinfo.expenses_monthly
                if self.userinfo.result.pension_started
                else self.savings
            ),
        }

    def goal_reached(self):
        """Determine if the target portfolio has been reached this month."""

        if (
            self.userinfo.current_portfolio > self.target_portfolio
            and not self.userinfo.result.pension_started
        ):
            return True

        return False

    def calculate_retirement(self):
        """
        Determines retirement age details.
        Should only run once, and only after self.goal_reached returns True.
        """

        # Make sure this method only runs once
        self.userinfo.result.pension_started = True

        # Remember the values from this first retirement month
        self.userinfo.result.months = self.count
        self.userinfo.result.years = self.userinfo.result.months // 12
        self.userinfo.result.age = (
            self.userinfo.current_year
            - self.userinfo.birth_year
            + self.userinfo.result.months // 12
        )
        self.userinfo.result.cost_of_living = round(self.userinfo.expenses_monthly * 12)
        self.userinfo.result.portfolio = round(self.userinfo.current_portfolio)

    def run(self):
        """Run monthly calculation for a set amount of cycles."""

        while self.count < 1200:
            # At the start of every year ..
            if (self.count % 12) == 0:
                self.yearly.start_year()
            self.count += 1

            # Calculate values for this month
            self.transactions()
            self.portfolio_values()

            if self.goal_reached():
                # Remember these values from this first retirement month
                self.calculate_retirement()

            # Store this month's value as graph data
            self.save()
            self.userinfo.result.graph_months.append(self.data)

            # Add month values to year tally and store end of the year
            # NOTE: year portfolio is added and in next step divided by
            #       12 to get the average portfolio size during the year.

            for key, value in self.data.items():
                self.yearly.data[key] += value
            if (self.count % 12) == 0:
                self.yearly.save(self.count)
                self.userinfo.result.graph_years.append(self.yearly.data)

            # Stop graph calculation after requested pension length
            if (
                self.userinfo.result.pension_started
                and self.count
                >= self.userinfo.result.months + 12 * self.userinfo.years_duration
            ):
                break


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

        # Extract userinfo input from data, and parse the values we'll need,
        # while initializing the results object structure.
        userinfo = UserInfo(data)

        # Initialize monthly calculator and yearly data object
        monthly_calculation = MonthCalculator(userinfo)

        # Run calculations and generate results
        monthly_calculation.run()

        # Convert Result() dataclass to a dictionary so it can be serialized to JSON
        return asdict(userinfo.result)
