"""
Test suite for calculations.py.

Run with:  pytest -v

Covers normal cases, edge cases, and invalid inputs for all three functions.
The business logic is tested in isolation — no HTTP layer involved.
"""

import pytest
from decimal import Decimal

from calculations import fibonacci, factorial, loan_repayment


# ---------------------------------------------------------------------------
# Fibonacci
# ---------------------------------------------------------------------------

class TestFibonacci:
    # Normal cases
    def test_sequence_start(self):
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        assert [fibonacci(i) for i in range(10)] == expected

    def test_larger_value(self):
        assert fibonacci(20) == 6765

    # Edge cases
    def test_zero(self):
        assert fibonacci(0) == 0

    def test_one(self):
        assert fibonacci(1) == 1

    # Invalid inputs
    def test_negative_raises_value_error(self):
        with pytest.raises(ValueError, match="non-negative"):
            fibonacci(-1)

    def test_float_raises_type_error(self):
        with pytest.raises(TypeError):
            fibonacci(3.5)

    def test_string_raises_type_error(self):
        with pytest.raises(TypeError):
            fibonacci("10")

    def test_bool_raises_type_error(self):
        # True == 1 and False == 0 in Python, but bool is not a valid index
        with pytest.raises(TypeError):
            fibonacci(True)


# ---------------------------------------------------------------------------
# Factorial
# ---------------------------------------------------------------------------

class TestFactorial:
    # Normal cases
    def test_small_value(self):
        assert factorial(5) == 120

    def test_known_value(self):
        assert factorial(10) == 3628800

    # Edge cases
    def test_zero(self):
        assert factorial(0) == 1

    def test_one(self):
        assert factorial(1) == 1

    def test_large_number(self):
        # Python handles arbitrary precision integers natively;
        # cross-check against the stdlib as a ground truth reference
        import math
        assert factorial(50) == math.factorial(50)
        assert factorial(100) == math.factorial(100)

    # Invalid inputs
    def test_negative_raises_value_error(self):
        with pytest.raises(ValueError, match="non-negative"):
            factorial(-1)

    def test_float_raises_type_error(self):
        with pytest.raises(TypeError):
            factorial(2.5)

    def test_string_raises_type_error(self):
        with pytest.raises(TypeError):
            factorial("5")

    def test_bool_raises_type_error(self):
        with pytest.raises(TypeError):
            factorial(False)


# ---------------------------------------------------------------------------
# Loan repayment
# ---------------------------------------------------------------------------

class TestLoanRepayment:
    # Normal cases
    def test_typical_loan(self):
        # £10,000 at 5% annual for 12 months → £856.07
        assert loan_repayment(10_000, 5, 12) == Decimal("856.07")

    def test_longer_term(self):
        # £200,000 at 3.5% annual for 360 months (30-year mortgage)
        result = loan_repayment(200_000, 3.5, 360)
        assert result == Decimal("898.09")

    def test_result_is_decimal(self):
        result = loan_repayment(5000, 4, 24)
        assert isinstance(result, Decimal)

    def test_result_has_two_decimal_places(self):
        result = loan_repayment(7500, 6, 36)
        assert result == result.quantize(Decimal("0.01"))

    # Edge cases
    def test_zero_interest_divides_evenly(self):
        assert loan_repayment(12_000, 0, 12) == Decimal("1000.00")

    def test_zero_interest_uneven(self):
        # 1000 over 3 months = 333.33
        assert loan_repayment(1000, 0, 3) == Decimal("333.33")

    def test_single_month(self):
        # One month: repay the whole principal (plus interest for that month)
        result = loan_repayment(1000, 12, 1)
        assert result == Decimal("1010.00")

    # Invalid inputs
    def test_negative_principal_raises(self):
        with pytest.raises(ValueError, match="[Pp]rincipal"):
            loan_repayment(-1000, 5, 12)

    def test_zero_principal_raises(self):
        with pytest.raises(ValueError, match="[Pp]rincipal"):
            loan_repayment(0, 5, 12)

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError, match="[Rr]ate"):
            loan_repayment(10_000, -1, 12)

    def test_zero_months_raises(self):
        with pytest.raises(ValueError, match="[Mm]onths"):
            loan_repayment(10_000, 5, 0)

    def test_negative_months_raises(self):
        with pytest.raises(ValueError, match="[Mm]onths"):
            loan_repayment(10_000, 5, -6)
