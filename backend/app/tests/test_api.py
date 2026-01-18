import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app, get_session, LoanScenario


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(test_engine):
    # Override DB session dependency to use in-memory DB
    def get_test_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    return TestClient(app)


def test_create_loan_returns_monthly_payment(client):
    payload = {"amount": 250000, "apr": 5.5, "term_months": 360}
    resp = client.post("/loans", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) == {"id", "amount", "apr", "term_months", "monthly_payment"}
    assert data["amount"] == 250000
    assert data["apr"] == 5.5
    assert data["term_months"] == 360
    # Verify monthly payment amount
    assert data["monthly_payment"] == 1419.47


def test_list_loans_orders_by_most_recent(client):
    client.post("/loans", json={"amount": 250000, "apr": 5.5, "term_months": 360})
    client.post("/loans", json={"amount": 150000, "apr": 4.25, "term_months": 180})
    resp = client.get("/loans")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    # Most recent first
    assert data[0]["amount"] == 150000
    assert data[0]["monthly_payment"] == 1128.42
    assert data[1]["amount"] == 250000
    assert data[1]["monthly_payment"] == 1419.47


def test_get_loan_detail_with_schedule_preview(client):
    create_resp = client.post("/loans", json={"amount": 250000, "apr": 5.5, "term_months": 360})
    loan_id = create_resp.json()["id"]
    resp = client.get(f"/loans/{loan_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == loan_id
    assert data["monthly_payment"] == 1419.47
    preview = data["schedule_preview"]
    assert isinstance(preview, list)
    assert len(preview) == 12
    # Check required keys are numeric
    first = preview[0]
    assert set(first.keys()) == {"month", "interest_paid", "principal_paid", "remaining_balance"}
    assert isinstance(first["month"], int)
    assert isinstance(first["interest_paid"], float)
    assert isinstance(first["principal_paid"], float)
    assert isinstance(first["remaining_balance"], float)


def test_get_loan_detail_404_when_missing(client):
    resp = client.get("/loans/9999")
    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "Loan not found"


def test_validation_rules(client):
    # amount must be > 0
    r1 = client.post("/loans", json={"amount": 0, "apr": 5.5, "term_months": 360})
    assert r1.status_code == 422
    # apr must be between 0 and 100
    r2 = client.post("/loans", json={"amount": 100000, "apr": -1, "term_months": 360})
    assert r2.status_code == 422
    r3 = client.post("/loans", json={"amount": 100000, "apr": 101, "term_months": 360})
    assert r3.status_code == 422
    # term_months between 1 and 480
    r4 = client.post("/loans", json={"amount": 100000, "apr": 5, "term_months": 0})
    assert r4.status_code == 422
    r5 = client.post("/loans", json={"amount": 100000, "apr": 5, "term_months": 481})
    assert r5.status_code == 422


def test_full_schedule_returned_for_short_term(client):
    # For term < 12, preview should be full term
    create_resp = client.post("/loans", json={"amount": 12000, "apr": 0, "term_months": 6})
    loan_id = create_resp.json()["id"]
    resp = client.get(f"/loans/{loan_id}")
    assert resp.status_code == 200
    data = resp.json()
    preview = data["schedule_preview"]
    assert len(preview) == 6
    # Check final remaining balance is 0.00
    assert preview[-1]["remaining_balance"] == 0.0
