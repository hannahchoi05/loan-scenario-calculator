import { useState, useEffect } from 'react';
import { PaymentCard } from './paymentCard';

export function SavedLoans() {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedLoan, setSelectedLoan] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const fetchLoans = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/loans');
      if (!response.ok) throw new Error('Failed to fetch loans');
      const data = await response.json();
      setLoans(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleViewLoan = async (loanId) => {
    try {
      const response = await fetch(`http://localhost:8000/loans/${loanId}`);
      if (!response.ok) throw new Error('Failed to fetch loan details');
      const data = await response.json();
      setSelectedLoan(data);
      setModalOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedLoan(null);
  };

  useEffect(() => {
    fetchLoans();
    
    // Subscribe to refresh events
    const handleRefresh = () => fetchLoans();
    window.addEventListener('loanCreated', handleRefresh);
    return () => window.removeEventListener('loanCreated', handleRefresh);
  }, []);

  if (loading && loans.length === 0) {
    return (
      <div className="saved-loans-section">
        <p className="text-center" style={{ color: '#718096' }}>Loading...</p>
      </div>
    );
  }

  if (loans.length === 0) {
    return (
      <div className="saved-loans-section">
        <h2 className="saved-loans-header">Saved Loan Scenarios</h2>
      </div>
    );
  }

  return (
    <div className="saved-loans-section">
      <h2 className="saved-loans-header">Saved Loan Scenarios</h2>
      
      {error && (
        <div style={{ marginBottom: '1rem', padding: '0.75rem', background: '#FEF2F2', border: '1px solid #FCA5A5', borderRadius: '4px', color: '#991B1B', fontSize: '0.875rem' }}>
          {error}
        </div>
      )}

      <table className="saved-loans-table">
        <thead>
          <tr>
            <th>Loan Amount</th>
            <th>APR</th>
            <th>Term</th>
            <th>Monthly Payment</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {loans.map((loan) => (
            <tr key={loan.id}>
              <td>${loan.amount.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</td>
              <td>{loan.apr.toFixed(2)}%</td>
              <td>{loan.term_months}</td>
              <td>${loan.monthly_payment.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
              <td>
                <button className="view-btn" onClick={() => handleViewLoan(loan.id)}>View</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Modal */}
      {modalOpen && selectedLoan && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>×</button>
            <div className="modal-header">
              <h3>Loan Details</h3>
              <p className="modal-loan-summary">
                ${selectedLoan.amount.toLocaleString('en-US', { minimumFractionDigits: 0 })} at {selectedLoan.apr}% APR for {selectedLoan.term_months} months
              </p>
            </div>
            <PaymentCard 
              monthlyPayment={selectedLoan.monthly_payment} 
              schedulePreview={selectedLoan.schedule_preview || []} 
            />
          </div>
        </div>
      )}
    </div>
  );
}
