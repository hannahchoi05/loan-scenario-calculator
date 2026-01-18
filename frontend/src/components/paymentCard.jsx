export function PaymentCard({ monthlyPayment, schedulePreview }) {
  return (
    <div className="card">
      <div className="results-section">
        <div className="results-title">Monthly Payment</div>
        <div className="monthly-payment">
          {monthlyPayment !== null
            ? `$${monthlyPayment.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
            : '$0.00'}
        </div>
      </div>

      {schedulePreview.length > 0 && (
        <div className="amortization-preview">
          <h3>Amortization Schedule Preview</h3>
          <div className="amortization-table-container">
            <table className="amortization-table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Interest Paid</th>
                  <th>Principal Paid</th>
                  <th>Remaining Balance</th>
                </tr>
              </thead>
              <tbody>
                {schedulePreview.slice(0, 12).map((entry) => (
                  <tr key={entry.month}>
                    <td>Month {entry.month}</td>
                    <td>
                      ${entry.interest_paid.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td>
                      ${entry.principal_paid.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td>
                      ${entry.remaining_balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
