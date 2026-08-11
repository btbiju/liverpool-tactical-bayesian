import { useState } from 'react';
import './App.css';
import { FixturesTab } from './tabs/FixturesTab.jsx';
import { SquadTab } from './tabs/SquadTab.jsx';
import { GamePlanTab } from './tabs/GamePlanTab.jsx';

const TABS = [
  { id: 'fixtures', label: 'Fixtures', render: () => <FixturesTab /> },
  { id: 'squad', label: 'Squad & Stats', render: () => <SquadTab /> },
  { id: 'gameplan', label: 'Game Plan', render: () => <GamePlanTab /> },
];

function App() {
  const [activeTab, setActiveTab] = useState('fixtures');
  const active = TABS.find((t) => t.id === activeTab) ?? TABS[0];

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header__inner">
          <div className="app-header__title">
            <span className="app-header__crest" aria-hidden="true">L</span>
            <div>
              <h1>Liverpool 2026/27 — Tactical Projection</h1>
              <p className="app-header__subtitle">
                Andoni Iraola's tactical identity, projected from a Bayesian prior and updated as the season plays out
              </p>
            </div>
          </div>
        </div>
        <nav className="tab-nav" aria-label="Dashboard sections">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`tab-nav__item${tab.id === activeTab ? ' tab-nav__item--active' : ''}`}
              aria-current={tab.id === activeTab ? 'page' : undefined}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>
      <main className="app-main">{active.render()}</main>
      <footer className="app-footer">
        <p>
          Portfolio project · Bayesian projection, not betting/wagering advice · data sourced from FotMob, official
          club statements, and football-data.org — see the project README for the full source hierarchy.
        </p>
      </footer>
    </div>
  );
}

export default App;
