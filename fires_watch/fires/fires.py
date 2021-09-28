import datetime
from dataclasses import asdict, dataclass


@dataclass
class Result:
    """
    Contains all calculated results.
    """

    cost_of_living: int
    portfolio: int
    months: int
    years: int
    age: int
    graph_months: object
    graph_years: object

    def __init__(self):
        self.cost_of_living = None
        self.portfolio = None
        self.months = None
        self.years = None
        self.age = None
        self.graph_months = []
        self.graph_years = []


class UserInfo:
    """Contains all initial user info, and the Result() class."""

    birth_year: int
    years_duration: int
    current_portfolio: int  # TODO: move to Result()
    initial_portfolio: int
    income_yearly: int
    income_monthly: int
    expenses_monthly: int
    savings_monthly: int
    inflation_percent_monthly: float
    portfolio_interest_percent_monthly: float
    safe_rate_yearly: float
    result: Result

    def __init__(self, data):
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
        # Initialize Result class
        self.result = Result()


class RetirementCalculator:
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
        self.current_year = datetime.date.today().year

    def goal_reached(self, target_portfolio):
        """Determine if the target portfolio has been reached this month."""

        if (
            self.userinfo.current_portfolio > target_portfolio
            and not self.pension_started
        ):
            return True

        return False

    # def calculate_result(self, months):
    def calculate_result(self, months):
        """
        Determines retirement age details.
        Should only run once, if self.goal_reached returns True.
        """

        self.pension_started = True

        # Remember these values from this first retirement month
        self.cost_of_living = round(self.userinfo.expenses_monthly * 12)
        self.portfolio = round(self.userinfo.current_portfolio)
        self.userinfo.result.months = months
        self.userinfo.result.years = self.userinfo.result.months // 12
        self.userinfo.result.age = (
            self.current_year
            - self.userinfo.birth_year
            + self.userinfo.result.months // 12
        )
        self.userinfo.result.cost_of_living = round(self.userinfo.expenses_monthly * 12)
        self.userinfo.result.portfolio = round(self.userinfo.current_portfolio)

    def calculate_result_new(self):
        # TODO
        self.userinfo.result.cost_of_living = round(self.userinfo.expenses_monthly * 12)
        self.userinfo.result.portfolio = round(self.userinfo.current_portfolio)


class MonthlyResults:
    """Calculates and tracks monthly results."""

    userinfo: UserInfo
    retirement: RetirementCalculator
    count: int
    interest: int
    savings: int
    target_portfolio: int
    month: object

    def __init__(self, userinfo, retirement):
        self.userinfo = userinfo
        self.retirement = retirement
        self.count = 0

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

    def save(self):

        # TODO

        # Store this month's value as graph data
        self.month = {
            "portfolio": round(self.userinfo.current_portfolio),
            "interest": round(self.interest),
            "change": round(
                -self.userinfo.expenses_monthly
                if self.retirement.pension_started
                else self.savings
            ),
        }


class YearlyResults:
    """Calculates and tracks yearly results."""

    year: object

    def start_year(self):
        self.year = {
            "portfolio": 0,
            "interest": 0,
            "change": 0,
        }

    def save(self, months):
        # TODO
        self.year = {
            "year": months / 12,
            "portfolio": self.year["portfolio"] // 12,
            "interest": round(self.year["interest"]),
            "change": round(self.year["change"]),
        }


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

        # Initialize retirement calculator
        retirement = RetirementCalculator(userinfo)

        # Initialize monthly and yearly calculators
        # TODO: should not need to pass retirement
        monthly = MonthlyResults(userinfo, retirement)
        yearly = YearlyResults()

        # Initialize some values to start our monthly calculation loop
        # TODO
        result = asdict(userinfo.result)

        # Run a monthly calculation, for a maximum of 100 years
        while monthly.count < 1200:
            # TODO
            # At the start of every year ..
            if (monthly.count % 12) == 0:
                yearly.start_year()
            monthly.count += 1

            # Calculate values for this month
            monthly.transactions()
            monthly.portfolio_values()

            if retirement.goal_reached(monthly.target_portfolio):

                # TODO
                # Remember these values from this first retirement month
                retirement.calculate_result(monthly.count)
                result["cost_of_living"] = retirement.cost_of_living
                result["portfolio"] = retirement.portfolio
                result["months"] = userinfo.result.months  # Months until retirement
                result["years"] = userinfo.result.years  # Truncate float to integer
                result["age"] = userinfo.result.age

            # TODO
            # Store this month's value as graph data
            monthly.save()
            month = monthly.month

            result["graph_months"].append(month)

            # Add month values to year tally and store end of the year
            # NOTE: year portfolio is added and in next step divided by
            #       12 to get the average portfolio size during the year.

            # TODO
            for key, value in month.items():
                yearly.year[key] += value
            if (monthly.count % 12) == 0:
                yearly.save(monthly.count)
                year = yearly.year
                result["graph_years"].append(year)

            # Stop graph calculation after requested pension length
            if (
                retirement.pension_started
                and monthly.count
                >= userinfo.result.months + 12 * userinfo.years_duration
            ):
                break

        # result = asdict(resultObject)
        return result
