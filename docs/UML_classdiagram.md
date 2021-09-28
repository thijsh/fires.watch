# Class Diagrams

```plantuml
@startuml

class Result {
    # cost_of_living
    # portfolio
    # months
    # years
    # age
    # pension_started
    # graph_months
    # graph_years
}

class UserInfo {
    # birth_year
    # years_duration
    # current_portfolio
    # initial_portfolio
    # income_yearly
    # income_monthly
    # expenses_monthly
    # savings_monthly
    # inflation_percent_monthly
    # portfolio_interest_percent_monthly
    # safe_rate_yearly
    # current_year
    # result
    
}

class YearCalculator {
    + start_year()
    + generate_yearly_data(months)
    + add_monthly_data(monthly_data)
}

class MonthCalculator {
    # userinfo
    # yearly
    # count
    # interest
    # savings
    # target_portfolio
    + calculate_transactions()
    + calculate_portfolio_values()
    + generate_monthly_data()
    + is_goal_reached()
    + calculate_retirement()
    + run()
}

note left of Result::stuff
    Example note
endnote

' Result " one-to- " *-- "one" UserInfo #line:blue;text:blue : **owner**


@enduml
```
