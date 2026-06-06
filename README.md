# Ikano Calculation Service

A small REST API that exposes three calculations: Fibonacci, Factorial, and Loan Repayment.

Built with Python 3.12 + FastAPI. Business logic is isolated from the HTTP layer so it can be tested and reused independently.

---

## Project structure

```
.
├── calculations.py      # pure business logic (no HTTP, no I/O)
├── app.py               # FastAPI HTTP wrapper
├── test_calculations.py # pytest test suite
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── scripts/
│   └── run-k8s-local.sh
├── kubernetes/
│   └── deployment.yaml
└── .github/
    └── workflows/
        └── ci.yml
```

## Running with Docker

```bash
# Build
docker build -t ikano-calc .

# Run
docker run -p 8000:8000 ikano-calc
```

The API is then available at `http://localhost:8000`.

---

## Kubernetes deployment

A minimal Kubernetes manifest is included in `kubernetes/deployment.yaml`. It creates:

- a `Deployment` with 3 replicas
- a `ClusterIP` service that load-balances traffic to the pods inside the cluster
- basic CPU/memory requests and limits
- liveness and readiness probes

A Deployment alone is not enough to access the app from your machine. The Deployment keeps the pods running; the Service gives those pods a stable internal endpoint; and for local development, `kubectl port-forward` maps that Service to a fixed localhost URL.

### Default local Minikube workflow

Use this workflow when running the Kubernetes version locally. It gives you a stable URL: `http://localhost:8000`.

```bash
# 1. Start Minikube
bash .scripts/run-k8s-local.sh

```

Now open:

```text
http://localhost:8000/docs
```

or test from another terminal:

```bash
curl "http://localhost:8000/fibonacci?n=10"
curl "http://localhost:8000/factorial?n=5"
curl -X POST "http://localhost:8000/loan"   -H "Content-Type: application/json"   -d '{"principal": 10000, "annual_rate": 5, "months": 12}'
```

## Automated validation with GitHub Actions

The repository includes `.github/workflows/ci.yml`. GitHub Actions runs automatically on:

- every pull request targeting `main`
- every push to `main`

The workflow performs a production-minded validation path:

1. Install Python dependencies.
2. Run the unit test suite with `pytest -v`.
3. Build the Docker image.
4. Start the application from the Docker image.
5. Smoke-test the live API endpoints:
   - `GET /fibonacci?n=10`
   - `GET /factorial?n=5`
   - `POST /loan`
6. Validate that the Kubernetes manifests are parseable with a client-side dry run.

This means a pull request does not only prove that the pure calculation functions work; it also proves that the service can be packaged into a container and started successfully.

The workflow intentionally does **not** deploy to a real Kubernetes cluster on every pull request. A real deployment would require a staging cluster, image registry credentials, rollout rules, and cleanup logic. For this assignment, the CI validates the Kubernetes YAML with a dry run and keeps actual cluster deployment as a separate release/staging concern.

To make this validation required before merging a pull request, enable a branch protection rule in GitHub:

1. Go to repository **Settings → Branches**.
2. Add a protection rule for `main`.
3. Enable **Require status checks to pass before merging**.
4. Select the CI status check from this workflow.

---

## API reference

### GET `/fibonacci?n=<int>`

Returns the nth Fibonacci number (0-indexed). The implementation uses the fast doubling algorithm.

```bash
curl "http://localhost:8000/fibonacci?n=10"
```
```json
{"n": 10, "result": 55}
```

```bash
# Invalid input → 400
curl "http://localhost:8000/fibonacci?n=-1"
```
```json
{"detail": "n must be non-negative, got -1"}
```

---

### GET `/factorial?n=<int>`

Returns n! (n factorial).

```bash
curl "http://localhost:8000/factorial?n=5"
```
```json
{"n": 5, "result": 120}
```

Large values are supported — Python integers are arbitrary-precision.

```bash
curl "http://localhost:8000/factorial?n=100"
```
```json
{"n": 100, "result": 93326215443944152681699238856266700490715968264381621468592963895217599993229915608941463976156518286253697920827223758251185210916864000000000000000000000000}
```

---

### POST `/loan`

Calculates the fixed monthly repayment using the standard annuity formula.

**Request body (JSON):**

| Field         | Type  | Description                              |
|---------------|-------|------------------------------------------|
| `principal`   | float | Loan amount (must be > 0)                |
| `annual_rate` | float | Annual interest rate as a percentage, e.g. `5` for 5% (must be ≥ 0) |
| `months`      | int   | Repayment term in months (must be > 0)   |

```bash
curl -X POST "http://localhost:8000/loan" \
  -H "Content-Type: application/json" \
  -d '{"principal": 10000, "annual_rate": 5, "months": 12}'
```
```json
{
  "principal": 10000.0,
  "annual_rate": 5.0,
  "months": 12,
  "monthly_repayment": 856.07
}
```

Zero-interest loan (principal divided equally):

```bash
curl -X POST "http://localhost:8000/loan" \
  -H "Content-Type: application/json" \
  -d '{"principal": 12000, "annual_rate": 0, "months": 12}'
```
```json
{"principal": 12000.0, "annual_rate": 0.0, "months": 12, "monthly_repayment": 1000.0}
```

---


## Fibonacci implementation

Fibonacci is implemented with the **fast doubling** algorithm instead of the simple iterative loop. The function computes a pair `(F(k), F(k+1))` and uses these identities:

```text
F(2k)     = F(k) × [2F(k+1) − F(k)]
F(2k + 1) = F(k)^2 + F(k+1)^2
```

Because each recursive call halves `n`, the recursion depth is approximately `log2(n)`. For example, calculating `fibonacci(1_000_000)` needs only about 20 recursive levels, not one million loop iterations.

The time complexity in terms of index steps is **O(log n)**. Python still has to allocate and multiply very large integers, so extremely large outputs can still be expensive because the result itself may contain many digits.

---
## Assumptions and limitations

- **Loan formula:** uses the standard fixed-rate annuity formula. Variable rates, balloon payments, and compound-frequency variations are not modelled.
- **Rounding:** loan repayments are rounded to 2 decimal places using ROUND_HALF_UP (standard banking convention). This means the final payment in a real amortisation schedule may differ by a few cents due to rounding accumulation — not accounted for here.
- **`annual_rate` is a percentage**, not a decimal: pass `5` for 5%, not `0.05`.
- **Fibonacci and Factorial inputs** must be plain integers. Floats and booleans are rejected even where the value would be valid (e.g. `fibonacci(True)` raises `TypeError`).
- **No authentication or rate limiting.** This is a demonstration service; add appropriate controls before any public deployment.
- **No persistence.** The service is stateless — results are computed on each request.
- **Kubernetes assumption:** the provided Kubernetes deployment assumes that load is distributed across more than one node. Running several replicas on the same small node can improve process resilience, but it does not create extra CPU capacity.
- **Kubernetes overhead:** for this small service, Kubernetes is only justified for learning, production-like delivery, or high/concurrent load. For low traffic, a single Docker container is simpler.
