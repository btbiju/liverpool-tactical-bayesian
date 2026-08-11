import { useAsync } from '../hooks/useAsync.js';
import { loadFixtures } from '../lib/dataLoaders.js';
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates.jsx';
import { Badge } from '../components/Badge.jsx';

const DATE_FMT = new Intl.DateTimeFormat('en-GB', {
  weekday: 'short',
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
});

function normalizeFixture(raw) {
  // Handles the raw football-data.org match shape from pipeline/fixtures_client.py.
  const home = raw.homeTeam?.name ?? raw.home?.name ?? 'Home TBD';
  const away = raw.awayTeam?.name ?? raw.away?.name ?? 'Away TBD';
  const isHome = home.includes('Liverpool');
  const opponent = isHome ? away : home;
  const date = raw.utcDate ?? raw.date ?? null;
  const status = raw.status ?? 'SCHEDULED';
  const competition = raw.competition?.name ?? raw.competition ?? null;
  const fullTime = raw.score?.fullTime;
  const result =
    fullTime && fullTime.home != null && fullTime.away != null
      ? { home: fullTime.home, away: fullTime.away }
      : null;
  return { id: raw.id ?? `${opponent}-${date}`, opponent, isHome, date, status, competition, result };
}

function statusTone(status) {
  if (status === 'FINISHED') return 'good';
  if (status === 'IN_PLAY' || status === 'LIVE' || status === 'PAUSED') return 'critical';
  if (status === 'POSTPONED' || status === 'CANCELLED') return 'warning';
  return 'neutral';
}

function FixtureRow({ fixture }) {
  const dateLabel = fixture.date ? DATE_FMT.format(new Date(fixture.date)) : 'Date TBD';
  return (
    <li className="fixture-row">
      <div className="fixture-row__date tabular-nums">{dateLabel}</div>
      <div className="fixture-row__match">
        <span className="fixture-row__venue">{fixture.isHome ? 'H' : 'A'}</span>
        <span className="fixture-row__opponent">{fixture.opponent}</span>
        {fixture.competition ? <span className="fixture-row__comp">{fixture.competition}</span> : null}
      </div>
      <div className="fixture-row__result">
        {fixture.result ? (
          <span className="tabular-nums">
            {fixture.result.home}–{fixture.result.away}
          </span>
        ) : (
          <Badge tone={statusTone(fixture.status)}>{fixture.status.replace('_', ' ')}</Badge>
        )}
      </div>
    </li>
  );
}

export function FixturesTab() {
  const { data, error, loading } = useAsync(loadFixtures);

  if (loading) return <LoadingState label="Loading fixtures…" />;
  if (error) return <ErrorState error={error} />;

  const fixtures = (data ?? []).map(normalizeFixture).sort((a, b) => new Date(a.date) - new Date(b.date));

  if (fixtures.length === 0) {
    return (
      <section>
        <div className="section-heading">
          <h2>Fixtures</h2>
        </div>
        <EmptyState>
          No fixture data pulled yet — the football-data.org client (
          <code>pipeline/fixtures_client.py</code>) is live-tested and working, it just hasn't been run to populate{' '}
          <code>data/fixtures/</code> yet. This tab will fill in automatically once that data exists.
        </EmptyState>
      </section>
    );
  }

  const upcoming = fixtures.filter((f) => f.status !== 'FINISHED');
  const finished = fixtures.filter((f) => f.status === 'FINISHED');

  return (
    <section>
      {upcoming.length > 0 && (
        <div style={{ marginBottom: 28 }}>
          <div className="section-heading">
            <h2>Upcoming</h2>
            <span className="section-heading__meta">{upcoming.length} fixtures</span>
          </div>
          <ul className="fixture-list card">
            {upcoming.map((f) => (
              <FixtureRow key={f.id} fixture={f} />
            ))}
          </ul>
        </div>
      )}
      {finished.length > 0 && (
        <div>
          <div className="section-heading">
            <h2>Results</h2>
            <span className="section-heading__meta">{finished.length} played</span>
          </div>
          <ul className="fixture-list card">
            {finished.map((f) => (
              <FixtureRow key={f.id} fixture={f} />
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
