"""Session 1.4: the Nova Travel refund rule as a plain Python function."""


def refund_amount(price, reason, days_before_trip):
    if reason == "airline cancelled":
        return price               # the airline cancels: full refund
    if days_before_trip > 14:
        return price - 50          # changed mind, more than 14 days before: minus a $50 fee
    return 0                       # changed mind, 14 days or less before: no refund


if __name__ == "__main__":
    print("Sara, airline cancelled, 9 days before: ", refund_amount(640.00, "airline cancelled", 9))
    print("Omar, changed mind, 30 days before:     ", refund_amount(380.00, "changed mind", 30))
    print("Omar, changed mind, 14 days before:     ", refund_amount(380.00, "changed mind", 14))
