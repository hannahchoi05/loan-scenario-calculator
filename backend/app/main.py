import os
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select

from app.calc import monthly_payment as calc_monthly_payment


# --- Database setup ---

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/loans")
engine = create_engine(DATABASE_URL, echo=False)


class LoanScenario(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	amount: float
	apr: float
	term_months: int
	monthly_payment: float
	created_at: datetime = Field(default_factory=datetime.utcnow)


def create_db_and_tables() -> None:
	SQLModel.metadata.create_all(engine)


def get_session():
	with Session(engine) as session:
		yield session


# --- Schemas ---

class LoanCreate(SQLModel):
	amount: Decimal = Field(gt=Decimal("0"))
	apr: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
	term_months: int = Field(ge=1, le=480)


from sqlmodel import SQLModel
from typing import List

class ScheduleItem(SQLModel):
    month: int
    interest_paid: float
    principal_paid: float
    remaining_balance: float

class LoanRead(SQLModel):
    id: int
    amount: float
    apr: float
    term_months: int
    monthly_payment: float

class LoanDetail(LoanRead):
    schedule_preview: List[ScheduleItem]

# --- App setup ---

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
	create_db_and_tables()


# --- Helpers ---

def compute_monthly_payment(amount: Decimal, apr: Decimal, term_months: int) -> Decimal:
	return calc_monthly_payment(amount=amount, apr_percent=apr, term_months=term_months)


def generate_schedule_preview(amount: Decimal, apr: Decimal, term_months: int) -> List[dict]:
	M = compute_monthly_payment(amount, apr, term_months)
	balance = amount
	schedule: List[dict] = []
	preview_months = min(term_months, 12)

	if apr == Decimal("0"):
		principal_month = (amount / Decimal(term_months))
		for m in range(1, preview_months + 1):
			interest_paid = Decimal("0.00")
			principal_paid = principal_month
			# rounding to cents
			interest_paid = interest_paid.quantize(Decimal("0.01"))
			principal_paid = principal_paid.quantize(Decimal("0.01"))
			balance = (balance - principal_paid).quantize(Decimal("0.01"))
			schedule.append(
				{
					"month": m,
					"interest_paid": float(interest_paid),
					"principal_paid": float(principal_paid),
					"remaining_balance": float(balance),
				}
			)
	else:
		r = apr / Decimal("100") / Decimal("12")
		for m in range(1, preview_months + 1):
			interest = (balance * r).quantize(Decimal("0.01"))
			principal = (M - interest).quantize(Decimal("0.01"))
			balance = (balance - principal).quantize(Decimal("0.01"))
			schedule.append(
				{
					"month": m,
					"interest_paid": float(interest),
					"principal_paid": float(principal),
					"remaining_balance": float(balance),
				}
			)
	return schedule


# --- Endpoints ---

@app.post("/loans/calculate", response_model=LoanDetail)
def calculate_loan(loan: LoanCreate):
	"""Calculate loan payment without saving to database"""
	mp = compute_monthly_payment(loan.amount, loan.apr, loan.term_months)
	schedule = generate_schedule_preview(loan.amount, loan.apr, loan.term_months)
	
	return LoanDetail(
		id=0,  # Not saved yet
		amount=float(loan.amount),
		apr=float(loan.apr),
		term_months=loan.term_months,
		monthly_payment=float(mp),
		schedule_preview=schedule,
	)


@app.post("/loans", response_model=LoanDetail)
def create_loan(loan: LoanCreate, session: Session = Depends(get_session)):
	# Compute monthly payment using Decimal for accuracy
	mp = compute_monthly_payment(loan.amount, loan.apr, loan.term_months)

	record = LoanScenario(
		amount=float(loan.amount),
		apr=float(loan.apr),
		term_months=loan.term_months,
		monthly_payment=float(mp),
	)
	session.add(record)
	session.commit()
	session.refresh(record)

	# Generate schedule preview
	schedule = generate_schedule_preview(loan.amount, loan.apr, loan.term_months)

	return LoanDetail(
		id=record.id,
		amount=record.amount,
		apr=record.apr,
		term_months=record.term_months,
		monthly_payment=record.monthly_payment,
		schedule_preview=schedule,
	)


@app.get("/loans", response_model=List[LoanRead])
def list_loans(session: Session = Depends(get_session)):
	statement = select(LoanScenario).order_by(LoanScenario.created_at.desc())
	results = session.exec(statement).all()
	return [
		LoanRead(
			id=r.id,
			amount=r.amount,
			apr=r.apr,
			term_months=r.term_months,
			monthly_payment=r.monthly_payment,
		)
		for r in results
	]


@app.get("/loans/{loan_id}", response_model=LoanDetail)
def get_loan(loan_id: int, session: Session = Depends(get_session)):
	record = session.get(LoanScenario, loan_id)
	if not record:
		raise HTTPException(status_code=404, detail="Loan not found")

	# Regenerate schedule preview from stored values
	schedule = generate_schedule_preview(
		amount=Decimal(str(record.amount)),
		apr=Decimal(str(record.apr)),
		term_months=record.term_months,
	)

	return LoanDetail(
		id=record.id,
		amount=record.amount,
		apr=record.apr,
		term_months=record.term_months,
		monthly_payment=record.monthly_payment,
		schedule_preview=schedule,
	)


@app.delete("/loans/{loan_id}")
def delete_loan(loan_id: int, session: Session = Depends(get_session)):
	record = session.get(LoanScenario, loan_id)
	if not record:
		raise HTTPException(status_code=404, detail="Loan not found")
	session.delete(record)
	session.commit()
	return {"message": "Loan deleted successfully"}
