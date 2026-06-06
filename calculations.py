from decimal import Decimal, ROUND_HALF_UP
import math

def fibonacci(n: int) -> int:

    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    def fibonacci_pair(k: int) -> tuple[int, int]:
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
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    return math.factorial(n)


def loan_repayment(principal: float, annual_rate: float, months: int) -> Decimal:

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
