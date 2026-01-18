import { useState } from 'react';
import { LoanForm } from './components/LoanForm';
import { SavedLoans } from './components/SavedLoans';

function App() {
  const [activeTab, setActiveTab] = useState('home');

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <span>Loan Scenario Calculator</span>
          </div>
          <nav className="header-nav">
            <a
              href="#home"
              onClick={(e) => { e.preventDefault(); setActiveTab('home'); }}
              className={`nav-link ${activeTab === 'home' ? 'active' : ''}`}
            >
              Home
            </a>
            <a
              href="#saved"
              onClick={(e) => { e.preventDefault(); setActiveTab('saved'); }}
              className={`nav-link ${activeTab === 'saved' ? 'active' : ''}`}
            >
              Saved Scenarios
            </a>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'home' && (
          <>
            <LoanForm />
            <SavedLoans />
          </>
        )}

        {activeTab === 'saved' && (
          <SavedLoans fullView={true} />
        )}
      </main>

    </div>
  );
}

export default App;
