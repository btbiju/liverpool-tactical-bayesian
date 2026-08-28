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

const UPDATED_FMT = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
});

function humanize(value) {
  if (!value) return null;
  return value
    .toLowerCase()
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function normalizeFixture(raw) {
  // Handles the raw football-data.org match shape from pipeline/fixtures_client.py.
  const homeTeam = raw.homeTeam ?? raw.home ?? { name: 'Home TBD' };
  const awayTeam = raw.awayTeam ?? raw.away ?? { name: 'Away TBD' };
  const home = homeTeam.name ?? 'Home TBD';
  const away = awayTeam.name ?? 'Away TBD';
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
  const liverpoolGoals = result ? (isHome ? result.home : result.away) : null;
  const opponentGoals = result ? (isHome ? result.away : result.home) : null;
  const outcome =
    liverpoolGoals == null || opponentGoals == null
      ? null
      : liverpoolGoals > opponentGoals
        ? 'W'
        : liverpoolGoals < opponentGoals
          ? 'L'
          : 'D';

  return {
    id: raw.id ?? `${opponent}-${date}`,
    opponent,
    isHome,
    date,
    status,
    competition,
    competitionCode: raw.competition?.code ?? null,
    result,
    outcome,
    homeTeam,
    awayTeam,
    halfTime: raw.score?.halfTime ?? null,
    duration: raw.score?.duration ?? null,
    matchday: raw.matchday ?? null,
    stage: raw.stage ?? null,
    referees: raw.referees ?? [],
    lastUpdated: raw.lastUpdated ?? null,
  };
}

// SCHEDULED (date set, kickoff time not yet confirmed) and TIMED (kickoff
// confirmed) are both just "normal upcoming fixture" -- showing a badge for
// either is redundant next to the date/time already in the row.
const NORMAL_UPCOMING_STATUSES = new Set(['SCHEDULED', 'TIMED']);

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
        ) : NORMAL_UPCOMING_STATUSES.has(fixture.status) ? (
          <span className="fixture-row__kickoff-set" aria-label="Kickoff confirmed">
            —
          </span>
        ) : (
          <Badge tone={statusTone(fixture.status)}>{fixture.status.replace('_', ' ')}</Badge>
        )}
      </div>
    </li>
  );
}

function ScoreTeam({ team, score }) {
  return (
    <div className="result-card__team">
      {team.crest ? <img className="result-card__crest" src={team.crest} alt="" /> : null}
      <div>
        <span className="result-card__team-name">{team.name}</span>
        {team.tla ? <span className="result-card__team-code">{team.tla}</span> : null}
      </div>
      <strong className="result-card__score tabular-nums">{score}</strong>
    </div>
  );
}

function DetailItem({ label, children }) {
  return (
    <div className="result-card__detail">
      <dt>{label}</dt>
      <dd>{children}</dd>
    </div>
  );
}

function FinishedFixtureCard({ fixture }) {
  const dateLabel = fixture.date ? DATE_FMT.format(new Date(fixture.date)) : 'Date not supplied';
  const halfTimeAvailable = fixture.halfTime?.home != null && fixture.halfTime?.away != null;
  const refereeNames = fixture.referees.map((referee) => referee.name).filter(Boolean);
  const outcomeLabel = fixture.outcome === 'W' ? 'Liverpool win' : fixture.outcome === 'L' ? 'Liverpool loss' : 'Draw';
  const outcomeTone = fixture.outcome === 'W' ? 'good' : fixture.outcome === 'L' ? 'critical' : 'neutral';

  return (
    <article className="result-card card">
      <div className="result-card__header">
        <div>
          <span className="result-card__date tabular-nums">{dateLabel}</span>
          <span className="result-card__competition">
            {fixture.competition ?? 'Competition not supplied'}
            {fixture.competitionCode ? ` · ${fixture.competitionCode}` : ''}
          </span>
        </div>
        <Badge tone={outcomeTone}>{outcomeLabel}</Badge>
      </div>

      <div className="result-card__scoreboard" aria-label={`Full time: ${fixture.homeTeam.name} ${fixture.result.home}, ${fixture.awayTeam.name} ${fixture.result.away}`}>
        <ScoreTeam team={fixture.homeTeam} score={fixture.result.home} />
        <ScoreTeam team={fixture.awayTeam} score={fixture.result.away} />
      </div>

      <dl className="result-card__details">
        <DetailItem label="Status">Full time</DetailItem>
        <DetailItem label="Matchweek">{fixture.matchday ?? 'Not supplied'}</DetailItem>
        <DetailItem label="Half-time score">
          {halfTimeAvailable ? `${fixture.halfTime.home}–${fixture.halfTime.away}` : 'Not supplied'}
        </DetailItem>
        <DetailItem label="Stage">{humanize(fixture.stage) ?? 'Not supplied'}</DetailItem>
        <DetailItem label="Duration">{humanize(fixture.duration) ?? 'Not supplied'}</DetailItem>
        <DetailItem label="Referee">{refereeNames.length > 0 ? refereeNames.join(', ') : 'Not supplied'}</DetailItem>
        <DetailItem label="Match ID">{fixture.id}</DetailItem>
        <DetailItem label="Source updated">
          {fixture.lastUpdated ? UPDATED_FMT.format(new Date(fixture.lastUpdated)) : 'Not supplied'}
        </DetailItem>
      </dl>
    </article>
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
  const finished = fixtures.filter((f) => f.status === 'FINISHED').reverse();

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
          <div className="result-list">
            {finished.map((f) => (
              <FinishedFixtureCard key={f.id} fixture={f} />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
