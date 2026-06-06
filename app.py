from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from calculations import fibonacci, factorial, loan_repayment

app = FastAPI(
    title="Ikano Calculation Service",
    description=(
        "Three calculations exposed as a minimal REST API: "
        "Fibonacci, Factorial, and Loan Repayment."
    ),
    version="1.0.0",
)

@app.get(
    "/fibonacci",
    summary="nth Fibonacci number",
    response_description="The nth Fibonacci number",
)
def get_fibonacci(
    n: int = Query(..., ge=0, description="Non-negative integer index"),
):
    """Return the nth Fibonacci number (0-indexed)."""
    try:
        return {"n": n, "result": fibonacci(n)}
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get(
    "/factorial",
    summary="Factorial of n",
    response_description="n!",
)
def get_factorial(
    n: int = Query(..., ge=0, description="Non-negative integer"),
):
    """Return n! (n factorial)."""
    try:
        return {"n": n, "result": factorial(n)}
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

class LoanRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Loan amount (must be positive)")
    annual_rate: float = Field(..., ge=0, description="Annual interest rate as a percentage, e.g. 5 for 5%")
    months: int = Field(..., gt=0, description="Repayment term in months")

    model_config = {
        "json_schema_extra": {
            "example": {
                "principal": 10000,
                "annual_rate": 5,
                "months": 12,
            }
        }
    }


@app.post(
    "/loan",
    summary="Monthly loan repayment",
    response_description="Fixed monthly repayment amount",
)
def calculate_loan(body: LoanRequest):
    """
    Calculate the fixed monthly repayment using the standard annuity formula.

    Zero-interest loans are handled as a special case (principal ÷ months).
    The result is rounded to two decimal places.
    """
    try:
        monthly = loan_repayment(body.principal, body.annual_rate, body.months)
        return {
            "principal": body.principal,
            "annual_rate": body.annual_rate,
            "months": body.months,
            "monthly_repayment": float(monthly),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
