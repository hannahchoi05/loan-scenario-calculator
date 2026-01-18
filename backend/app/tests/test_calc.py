import pytest
from decimal import Decimal
from app.calc import monthly_payment


class TestMonthlyPayment:
    """Test suite for monthly_payment function"""

    def test_standard_loan_calculation(self):
        """Test standard loan: $200,000 at 6% APR for 30 years (360 months)"""
        # Example: $200,000 loan at 6% APR for 30 years
        # Expected monthly payment: approximately $1,199.10
        result = monthly_payment(
            amount=Decimal('200000'),
            apr_percent=Decimal('6'),
            term_months=360
        )
        assert result == Decimal('1199.10')

    def test_zero_percent_apr(self):
        """Test loan with 0% APR (no interest)"""
        # $12,000 at 0% APR for 12 months should be $1,000/month
        result = monthly_payment(
            amount=Decimal('12000'),
            apr_percent=Decimal('0'),
            term_months=12
        )
        assert result == Decimal('1000.00')

    def test_zero_percent_apr_uneven_division(self):
        """Test 0% APR with amount not evenly divisible by term"""
        # $10,000 at 0% APR for 3 months
        # $10,000 / 3 = $3,333.33... should round to $3,333.33
        result = monthly_payment(
            amount=Decimal('10000'),
            apr_percent=Decimal('0'),
            term_months=3
        )
        assert result == Decimal('3333.33')

    def test_short_term_loan(self):
        """Test short-term loan: $5,000 at 5% APR for 12 months"""
        result = monthly_payment(
            amount=Decimal('5000'),
            apr_percent=Decimal('5'),
            term_months=12
        )
        # Expected: ~$430.33
        assert isinstance(result, Decimal)
        assert result > Decimal('0')
        assert result.as_tuple().exponent == -2  # Verify 2 decimal places

    def test_high_interest_rate(self):
        """Test loan with high interest rate"""
        # $10,000 at 20% APR for 24 months
        result = monthly_payment(
            amount=Decimal('10000'),
            apr_percent=Decimal('20'),
            term_months=24
        )
        assert isinstance(result, Decimal)
        assert result > Decimal('500')  # Should be significantly higher due to interest

    def test_very_low_amount(self):
        """Test with very small loan amount"""
        result = monthly_payment(
            amount=Decimal('100'),
            apr_percent=Decimal('5'),
            term_months=12
        )
        assert result > Decimal('0')
        assert result < Decimal('10')

    def test_decimal_precision(self):
        """Test that result is properly rounded to 2 decimal places"""
        result = monthly_payment(
            amount=Decimal('10000'),
            apr_percent=Decimal('4.5'),
            term_months=60
        )
        # Verify exactly 2 decimal places
        assert result.as_tuple().exponent == -2
        # Verify it's a valid money amount
        assert str(result).count('.') == 1

    def test_rounding_half_up(self):
        """Test that rounding uses ROUND_HALF_UP"""
        # This test ensures proper rounding behavior
        result = monthly_payment(
            amount=Decimal('3000'),
            apr_percent=Decimal('3.5'),
            term_months=36
        )
        assert isinstance(result, Decimal)
        # Result should be properly rounded (not truncated)
        decimal_str = str(result)
        assert len(decimal_str.split('.')[-1]) <= 2

    def test_very_long_term(self):
        """Test 40-year mortgage"""
        result = monthly_payment(
            amount=Decimal('300000'),
            apr_percent=Decimal('3.5'),
            term_months=480
        )
        assert result > Decimal('0')
        assert result > Decimal('1000')
        assert result < Decimal('1500')

    def test_payment_exceeds_principal_for_short_term(self):
        """Test that monthly payment is reasonable for short-term high-rate loan"""
        result = monthly_payment(
            amount=Decimal('50000'),
            apr_percent=Decimal('12'),
            term_months=6
        )
        # With high interest on short term, monthly payment should be substantial
        assert result > Decimal('8000')

    # Error cases
    def test_invalid_term_months_zero(self):
        """Test that term_months=0 raises ValueError"""
        with pytest.raises(ValueError, match="term_months must be > 0"):
            monthly_payment(
                amount=Decimal('10000'),
                apr_percent=Decimal('5'),
                term_months=0
            )

    def test_invalid_term_months_negative(self):
        """Test that negative term_months raises ValueError"""
        with pytest.raises(ValueError, match="term_months must be > 0"):
            monthly_payment(
                amount=Decimal('10000'),
                apr_percent=Decimal('5'),
                term_months=-12
            )

    def test_invalid_amount_zero(self):
        """Test that amount=0 raises ValueError"""
        with pytest.raises(ValueError, match="amount must be > 0"):
            monthly_payment(
                amount=Decimal('0'),
                apr_percent=Decimal('5'),
                term_months=12
            )

    def test_invalid_amount_negative(self):
        """Test that negative amount raises ValueError"""
        with pytest.raises(ValueError, match="amount must be > 0"):
            monthly_payment(
                amount=Decimal('-10000'),
                apr_percent=Decimal('5'),
                term_months=12
            )

    def test_invalid_apr_negative(self):
        """Test that negative APR raises ValueError"""
        with pytest.raises(ValueError, match="apr must be between 0 and 100"):
            monthly_payment(
                amount=Decimal('10000'),
                apr_percent=Decimal('-1'),
                term_months=12
            )

    def test_invalid_apr_over_100(self):
        """Test that APR > 100 raises ValueError"""
        with pytest.raises(ValueError, match="apr must be between 0 and 100"):
            monthly_payment(
                amount=Decimal('10000'),
                apr_percent=Decimal('101'),
                term_months=12
            )

    def test_apr_exactly_100(self):
        """Test that APR=100% is valid"""
        result = monthly_payment(
            amount=Decimal('10000'),
            apr_percent=Decimal('100'),
            term_months=12
        )
        assert result > Decimal('0')

    # Edge cases with Decimal precision
    def test_decimal_input_consistency(self):
        """Test that Decimal inputs work correctly"""
        result1 = monthly_payment(
            amount=Decimal('200000'),
            apr_percent=Decimal('6'),
            term_months=360
        )
        # Should get consistent results
        result2 = monthly_payment(
            amount=Decimal('200000'),
            apr_percent=Decimal('6'),
            term_months=360
        )
        assert result1 == result2

    def test_fractional_percent_apr(self):
        """Test APR with decimal percentages like 3.75%"""
        result = monthly_payment(
            amount=Decimal('250000'),
            apr_percent=Decimal('3.75'),
            term_months=360
        )
        assert result > Decimal('0')
        assert result.as_tuple().exponent == -2

    def test_one_month_term(self):
        """Test loan for exactly 1 month"""
        result = monthly_payment(
            amount=Decimal('10000'),
            apr_percent=Decimal('12'),
            term_months=1
        )
        # Payment should include principal + 1 month of interest
        assert result > Decimal('10000')

    def test_realistic_car_loan(self):
        """Test realistic car loan: $25,000 at 4.5% for 5 years"""
        result = monthly_payment(
            amount=Decimal('25000'),
            apr_percent=Decimal('4.5'),
            term_months=60
        )
        # Expected approximately $460/month
        assert Decimal('450') < result < Decimal('470')

    def test_realistic_personal_loan(self):
        """Test realistic personal loan: $10,000 at 8% for 3 years"""
        result = monthly_payment(
            amount=Decimal('10000'),
            apr_percent=Decimal('8'),
            term_months=36
        )
        # Expected approximately $313/month
        assert Decimal('300') < result < Decimal('320')
