# Loan Scenario Calculator

A loan scenario calculator application for calculating and managing loan scenarios with amortization schedules.

## Project Overview

This Loan Scenario Calculator allows users to:
1. Enter loan details (amount, interest rate, term)
2. See the calculated monthly payment
3. View a preview of the amortization schedule of the first 12 months (or full schedule if loan term is less than 12 months)
4. Save loan scenarios
5. View previously saved scenarios
6. Delete saved scenarios

## Tech Stack

### Backend
- Language: **Python 3.11**
- Framework: **FastAPI**
- Database: **PostgreSQL**
- Persistence: **SQLModel**
- Web Server: **Uvicorn**

### Frontend
- UI library: **React 19**
- Build: **Vite**

### DevOps
- Containerization: **Docker**

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional)

### Option 1: Docker

```bash
# Build and run with Docker Compose
docker compose up
```

### Option 2

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

The frontend will be available at `http://localhost:5173` and the backend at `http://localhost:8000`.

## How to Run Tests

### Backend Tests

```bash
cd backend
source .venv/bin/activate
pytest app/tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/loans/calculate` | Calculates a new loan scenario |
| POST | `/loans` | Create a new loan scenario |
| GET | `/loans` | List all saved loan scenarios |
| GET | `/loans/{id}` | Get loan details with amortization schedule |
| DELETE | `/loans/{id}` | Delete a loan scenario |

The Fast-API Swagger UI, which is available at `http://127.0.0.1:8000/docs#/` once application is running, can be used to test the API endpoints. 


## Technical Details

### Loan Calculation Approach

The monthly payment is calculated using the standard amortization formula:

$$M = P \times \frac{r(1+r)^n}{(1+r)^n - 1}$$

Where:
- **M** = Monthly payment
- **P** = Principal (loan amount)
- **r** = Monthly interest rate (APR ÷ 12 ÷ 100)
- **n** = Total number of payments (term in months)

For **0% APR loans**, the formula simplifies to:
$$M = \frac{P}{n}$$

### Rounding Approach

All monetary calculations use Python's `decimal.Decimal` type with:
- **Precision**: 28 significant digits for intermediate calculations
- **Rounding**: `ROUND_HALF_UP` methodology to 2 decimal places (cents)
- **Consistency**: All displayed values and stored amounts are rounded to cents

### Tradeoffs and Assumptions

1. **12-Month Preview**: Amortization schedules show only the first 12 months to balance detail with performance. Full schedules could be added as a separate endpoint.

2. **No Authentication**: The current implementation has no user authentication. All users share the same loan scenarios.

3. **APR vs. APY**: The calculator uses APR (Annual Percentage Rate) with simple monthly compounding, not APY. This matches standard mortgage calculations.

4. **Rounding at Each Step**: Interest and principal are rounded at each month's calculation, which may result in a small discrepancy in the final payment. This matches real-world loan statements.
