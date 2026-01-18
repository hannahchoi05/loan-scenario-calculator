import { useState } from 'react';
import { PaymentCard } from './paymentCard';

export function LoanForm() {
  const [amount, setAmount] = useState('');
  const [apr, setApr] = useState('');
  const [term, setTerm] = useState('');
  const [monthlyPayment, setMonthlyPayment] = useState(null);
  const [schedulePreview, setSchedulePreview] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const newErrors = {};

    const amountNum = parseFloat(amount);
    if (!amount || isNaN(amountNum) || amountNum <= 0) {
      newErrors.amount = 'Loan amount must be greater than 0.';
    }

    const aprNum = parseFloat(apr);
    if (!apr || isNaN(aprNum) || aprNum < 0 || aprNum > 100) {
      newErrors.apr = 'Interest rate must be between 0 and 100.';
    }

    const termNum = parseInt(term);
    if (!term || isNaN(termNum) || termNum <= 0 || termNum > 480 || !Number.isInteger(parseFloat(term))) {
      newErrors.term = 'Loan term must be between 1 and 480 months.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCalculate = async (e) => {
    e.preventDefault();

    if (!validate()) {
      setMonthlyPayment(null);
      setSchedulePreview([]);
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const response = await fetch('http://localhost:8000/loans', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: parseFloat(amount),
          apr: parseFloat(apr),
          term_months: parseInt(term),
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to calculate loan payment');
      }

      const data = await response.json();
      setMonthlyPayment(data.monthly_payment);
      setSchedulePreview(data.schedule_preview || []);

      // Dispatch event to refresh saved loans list
      window.dispatchEvent(new Event('loanCreated'));
    } catch (err) {
      setErrors({
        server: err instanceof Error ? err.message : 'Unknown error',
      });
      setMonthlyPayment(null);
      setSchedulePreview([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="loan-calculator-section">
      {/* Left Column - Form */}
      <div className="card">
        <h2 className="card-title">New Loan Scenario</h2>

        <form onSubmit={handleCalculate}>
          <div className="form-group">
            <label htmlFor="amount" className="form-label">
              Loan Amount
            </label>
            <div className="input-with-prefix">
              <span className="input-prefix">$</span>
              <input
                type="number"
                id="amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                disabled={loading}
                className="form-input"
                placeholder="250,000"
                step="1"
              />
            </div>
            {errors.amount && <p className="error-message">{errors.amount}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="apr" className="form-label">
              Interest Rate (APR)
            </label>
            <div className="input-with-suffix">
              <input
                type="number"
                id="apr"
                value={apr}
                onChange={(e) => setApr(e.target.value)}
                disabled={loading}
                className="form-input"
                placeholder="5.5"
                step="0.1"
              />
              <span className="input-suffix">%</span>
            </div>
            {errors.apr && <p className="error-message">{errors.apr}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="term" className="form-label">
              Loan Term (Months)
            </label>
            <input
              type="number"
              id="term"
              value={term}
              onChange={(e) => setTerm(e.target.value)}
              disabled={loading}
              className="form-input"
              placeholder="360"
              step="1"
            />
            {errors.term && <p className="error-message">{errors.term}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Calculating...' : 'Calculate & Save'}
          </button>
        </form>
      </div>

      {/* Right Column - Results */}
      <PaymentCard monthlyPayment={monthlyPayment} schedulePreview={schedulePreview} />
    </div>
  );
}
