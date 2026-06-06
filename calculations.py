"""
Core calculation functions.

All business logic lives here, isolated from I/O and HTTP concerns.
Each function validates its own inputs and raises ValueError or TypeError
with a descriptive message — errors are handled once, at the source.
"""

from decimal import Decimal, ROUND_HALF_UP


def fibonacci(n: int) -> int:
    """
    Return the nth Fibonacci number using the fast doubling algorithm.

    fibonacci(0) → 0
    fibonacci(1) → 1
    fibonacci(6) → 8

    Fast doubling computes the pair (F(k), F(k+1)) and uses identities
    that jump from k to 2k, so the number of recursive steps is O(log n)
    instead of O(n).

    Raises:
        TypeError:  if n is not an integer
        ValueError: if n is negative
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    def fibonacci_pair(k: int) -> tuple[int, int]:
        """Return (F(k), F(k+1))."""
        if k == 0:
            return 0, 1

        a, b = fibonacci_pair(k // 2)
        c = a * (2 * b - a)      # F(2k)
        d = a * a + b * b        # F(2k + 1)

        if k % 2 == 0:
            return c, d
        return d, c + d

    return fibonacci_pair(n)[0]


def factorial(n: int) -> int:
    """
    Return n! (n factorial).

    factorial(0) → 1
    factorial(5) → 120

    Python integers are arbitrary-precision, so large values are fine.

    Raises:
        TypeError:  if n is not an integer
        ValueError: if n is negative
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def loan_repayment(principal: float, annual_rate: float, months: int) -> Decimal:
    """
    Calculate the fixed monthly repayment for a loan.

    Formula: M = P × [r(1+r)^n / ((1+r)^n − 1)]
    where r = monthly interest rate (annual_rate / 1200),
          n = number of months,
          P = principal.

    For zero-interest loans the formula degenerates; repayment = P / n.
    All arithmetic uses Decimal to avoid floating-point drift on money.

    Args:
        principal:   loan amount (must be > 0)
        annual_rate: annual interest rate as a percentage, e.g. 5 for 5%
                     (must be ≥ 0)
        months:      repayment term in months (must be > 0)

    Returns:
        Monthly repayment rounded to 2 decimal places (Decimal).

    Raises:
        ValueError: on invalid inputs
    """
    try:
        P = Decimal(str(principal))
        r_annual = Decimal(str(annual_rate))
        n = int(months)
    except Exception as exc:
        raise ValueError(f"Invalid loan parameters: {exc}") from exc

    if P <= 0:
        raise ValueError(f"Principal must be positive, got {principal}")
    if r_annual < 0:
        raise ValueError(f"Annual rate must be non-negative, got {annual_rate}")
    if n <= 0:
        raise ValueError(f"Months must be a positive integer, got {months}")

    if r_annual == 0:
        monthly = P / n
    else:
        r = r_annual / Decimal("1200")          # annual % → monthly decimal
        factor = (Decimal("1") + r) ** n
        monthly = P * (r * factor) / (factor - Decimal("1"))

    return monthly.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
