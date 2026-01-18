from decimal import Decimal, getcontext, ROUND_HALF_UP

# set precision high enough for intermediate calculations
getcontext().prec = 28

def monthly_payment(amount: Decimal, apr_percent: Decimal, term_months: int) -> Decimal:
    """
    Calculate monthly payment and return Decimal rounded to cents (ROUND_HALF_UP).
    Handles 0% APR specially.
    """
    if term_months <= 0:
        raise ValueError("term_months must be > 0")
    if amount <= 0:
        raise ValueError("amount must be > 0")
    if apr_percent < 0 or apr_percent > 100:
        raise ValueError("apr must be between 0 and 100")

    P = amount
    if apr_percent == Decimal('0'):
        # no interest
        M = P / Decimal(term_months)
    else:
        r = apr_percent / Decimal('100') / Decimal('12')  # monthly rate as Decimal
        n = Decimal(term_months)
        M = (P * r) / (1 - (1 + r) ** (-n))

    # round to cents
    return M.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def amortization_preview(amount: Decimal, apr_percent: Decimal, term_months: int, preview_months: int = 12):
    M = monthly_payment(amount, apr_percent, term_months)
    balance = amount
    schedule = []
    if apr_percent == Decimal('0'):
        for m in range(1, min(term_months, preview_months)+1):
            principal_paid = (amount / Decimal(term_months)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            interest_paid = Decimal('0.00')
            balance = (balance - principal_paid).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            schedule.append({
                "month": m,
                "interest_paid": f"{interest_paid}",
                "principal_paid": f"{principal_paid}",
                "remaining_balance": f"{balance}"
            })
    else:
        r = apr_percent / Decimal('100') / Decimal('12')
        for m in range(1, min(term_months, preview_months)+1):
            interest = (balance * r).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            principal = (M - interest).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            balance = (balance - principal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            schedule.append({
                "month": m,
                "interest_paid": f"{interest}",
                "principal_paid": f"{principal}",
                "remaining_balance": f"{balance}"
            })
    return schedule
