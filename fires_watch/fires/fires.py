import datetime
from dataclasses import asdict, dataclass
from typing import List


@dataclass
class Result:
    """
    Contains all results we want to return.
    Dataclass, so it can be converted into a dictionary for serializing.

    At the moment retirement is reached, the following variables are recorded:
    - cost_of_living
    - portfolio
    - months
    - years
    - age
    """

    cost_of_living: float
    portfolio: float
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
    yearly_income: int
    monthly_income: int
    monthly_expenses: int
    monthly_savings: int
    inflation_percent_monthly: float
    portfolio_interest_percent_monthly: float
    safe_rate_yearly: float
    current_year: int

    def __init__(self, data):
        """Parse user input and determine initial values."""

        self.birth_year = data["birth_year"]
        self.years_duration = data["years_duration"]
        self.initial_portfolio = data["portfolio_value"]
        self.current_portfolio = self.initial_portfolio
        self.yearly_income = data["income_gross_per_year"]
        self.monthly_income = self.yearly_income / 12
        self.monthly_expenses = data["expenses_per_year"] / 12
        self.monthly_savings = max(self.monthly_income - self.monthly_expenses, 0)
        self.inflation_percent_monthly = (
            1 + data["inflation_percentage_per_year"] / 100
        ) ** (1 / 12)
        self.portfolio_interest_percent_monthly = (
            1 + data["portfolio_percentage_per_year"] / 100
        ) ** (1 / 12)
        self.safe_rate_yearly = data["max_withdrawal_percentage_per_year"] / 100
        self.current_year = datetime.date.today().year


class Calculator:
    """Calculates and tracks monthly results."""

    userinfo: UserInfo
    result: Result
    month_count: int
    monthly_interest: float
    monthly_savings: float
    target_portfolio: float
    yearly_data: object

    def __init__(self, userinfo, result):
        """Set initial values"""
        self.userinfo = userinfo
        self.result = result
        self.month_count = 0

    def start_year(self):
        """Set yearly values to zero at the start of the year."""
        self.yearly_data = {
            "portfolio": 0,
            "interest": 0,
            "change": 0,
        }

    def generate_yearly_data(self, months):
        """Save the yearly totals for further processing."""

        # NOTE: Yearly portfolio is added and divided by 12 to get the
        #       average portfolio size during the year.

        return {
            "year": months / 12,
            "portfolio": self.yearly_data["portfolio"] // 12,
            "interest": round(self.yearly_data["interest"]),
            "change": round(self.yearly_data["change"]),
        }

    def add_monthly_to_yearly_data(self, monthly_data):
        for key, value in monthly_data.items():
            self.yearly_data[key] += value

    def calculate_monthly_transactions(self):
        """
        Calculate monthly transaction values:
        - Expenses
        - Interest
        - Savings
        """
        # NOTE:
        # We save the income - expenses, and to err on the safe side of
        # caution the expenses are inflation adjusted but income isn't
        # (because it often lags behind inflation because capitalism).
        # This results in the possibility of savings to go into negative
        # numbers after years/decades (essentially depleting the
        # portfolio before pension start) and this is also not
        # representative of reality we place a lower bound on the
        # monthly savings of at least zero.
        self.userinfo.monthly_expenses *= self.userinfo.inflation_percent_monthly
        self.monthly_interest = self.userinfo.current_portfolio * (
            self.userinfo.portfolio_interest_percent_monthly - 1
        )
        self.monthly_savings = max(
            self.userinfo.monthly_income - self.userinfo.monthly_expenses, 0
        )

    def calculate_monthly_portfolio_values(self):
        """
        Calculate this month's portfolio values:
        - Current portfolio value (based on interest and savings)
        - Target portfolio (based on 'safe' withdrawal rate)
        """
        self.userinfo.current_portfolio = (
            self.userinfo.current_portfolio
            * self.userinfo.portfolio_interest_percent_monthly
            + self.monthly_savings
        )
        self.target_portfolio = (
            self.userinfo.monthly_expenses * 12 / self.userinfo.safe_rate_yearly
        )

    def generate_monthly_data(self):
        """Store monthly results for further processing."""
        return {
            "portfolio": round(self.userinfo.current_portfolio),
            "interest": round(self.monthly_interest),
            "change": round(
                -self.userinfo.monthly_expenses
                if self.result.pension_started
                else self.monthly_savings
            ),
        }

    def is_retirement_goal_reached(self):
        """Determine if the target portfolio has been reached this month."""
        return (
            self.userinfo.current_portfolio > self.target_portfolio
            and not self.result.pension_started
        )

    def calculate_retirement_values(self):
        """
        Determines retirement age details.
        Should only run once, and only after self.is_retirement_goal_reached returns True.
        """

        # Make sure this method only runs once
        self.result.pension_started = True

        # Remember the values from this first retirement month
        self.result.months = self.month_count
        self.result.years = self.result.months // 12
        self.result.age = (
            self.userinfo.current_year
            - self.userinfo.birth_year
            + self.result.months // 12
        )
        self.result.cost_of_living = round(self.userinfo.monthly_expenses * 12)
        self.result.portfolio = round(self.userinfo.current_portfolio)

    def run(self):
        """Run monthly calculation for a set amount of cycles."""

        while self.month_count < 1200:
            # At the start of every year ..
            if (self.month_count % 12) == 0:
                self.start_year()
            self.month_count += 1

            # Calculate values for this month
            self.calculate_monthly_transactions()
            self.calculate_monthly_portfolio_values()

            if self.is_retirement_goal_reached():
                # Save values from the first retirement month
                self.calculate_retirement_values()

            # Store this month's value as graph data
            monthly_data = self.generate_monthly_data()
            self.result.graph_months.append(monthly_data)

            # Add monthly values to year tally and store at end of year
            self.add_monthly_to_yearly_data(monthly_data)

            if (self.month_count % 12) == 0:
                yearly_data = self.generate_yearly_data(self.month_count)
                self.result.graph_years.append(yearly_data)

            # Stop graph calculation after requested pension length
            if (
                self.result.pension_started
                and self.month_count
                >= self.result.months + 12 * self.userinfo.years_duration
            ):
                break

    def results_as_dict(self):
        return asdict(self.result)


class Fires:
    @staticmethod
    def calculate(data):
        """
        Calculate monthly portfolio value by:
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

        Generated datasets meant for graphing:
        - Monthly
        - Yearly

        For each datapoint in a dataset, we return (at that point in time):
        - Total portfolio value
        - Total interest value
        - Total change (result of expenses, savings, withdrawal rate)
        """

        # Initialize Result dataclass object
        result = Result()

        # Parse user input
        userinfo = UserInfo(data)

        # Initialize calculator
        calculator = Calculator(userinfo, result)

        # Run calculations and generate results
        calculator.run()

        # Convert Result() dataclass to a dictionary so it can be
        # serialized to JSON
        return calculator.results_as_dict()
