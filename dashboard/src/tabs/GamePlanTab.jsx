import { useAsync } from '../hooks/useAsync.js';
import {
  loadLineupProjection,
  loadManagerPrior,
  loadPosteriors,
  loadPlayerProfiles,
} from '../lib/dataLoaders.js';
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates.jsx';
import { StatTile } from '../components/StatTile.jsx';
import { PredictedLineup } from './PredictedLineup.jsx';

const METRIC_DISPLAY = {
  possession_pct: { label: 'Possession', unit: '%', decimals: 1 },
  ppda: { label: 'PPDA (pressing)', unit: '', decimals: 2 },
  shots_on_target_per_match: { label: 'Shots on target', unit: '/match', decimals: 2 },
  goals_conceded_per_match: { label: 'Goals conceded', unit: '/match', decimals: 2 },
  accurate_passes_per_match: { label: 'Accurate passes', unit: '/match', decimals: 0 },
  accurate_crosses_per_match: { label: 'Accurate crosses', unit: '/match', decimals: 2 },
};

function fmt(value, decimals) {
  return Number(value).toFixed(decimals);
}

function FormationBars({ formationPrior }) {
  const alpha = formationPrior?.alpha ?? {};
  const total = Object.values(alpha).reduce((sum, v) => sum + v, 0) || 1;
  const rows = Object.entries(alpha).sort((a, b) => b[1] - a[1]);

  return (
    <div>
      {rows.map(([formation, weight]) => {
        const pct = (weight / total) * 100;
        return (
          <div className="metric-bar-row" key={formation}>
            <div className="metric-bar-row__label">{formation}</div>
            <div className="metric-bar-track">
              <div className="metric-bar-track__fill" style={{ '--fill': `${pct}%` }} />
            </div>
            <div className="metric-bar-row__value tabular-nums">{pct.toFixed(0)}%</div>
          </div>
        );
      })}
    </div>
  );
}

function XgTrend({ seasonXg }) {
  const seasons = Object.entries(seasonXg ?? {});
  const max = Math.max(...seasons.map(([, s]) => s.value ?? 0), 1);
  return (
    <div>
      {seasons.map(([season, s]) => (
        <div className="metric-bar-row" key={season}>
          <div className="metric-bar-row__label">{season}</div>
          <div className="metric-bar-track">
            <div className="metric-bar-track__fill" style={{ '--fill': `${((s.value ?? 0) / max) * 100}%` }} />
          </div>
          <div className="metric-bar-row__value tabular-nums">
            {s.value != null ? s.value.toFixed(1) : '—'}
            {s.confidence && s.confidence !== 'confirmed' ? (
              <span className="modal-panel__muted"> ({s.confidence})</span>
            ) : null}
          </div>
        </div>
      ))}
    </div>
  );
}

function PosteriorPanel({ posteriors, prior }) {
  const latest = [...posteriors].sort((a, b) => b.as_of_matchweek - a.as_of_matchweek)[0];
  const updatedMetrics = Object.entries(latest.continuous_metrics ?? {});
  const updates = latest.update_log ?? [];

  return (
    <div className="posterior-panel">
      <div className="posterior-panel__summary card">
        <div>
          <span className="posterior-panel__eyebrow">Current model state</span>
          <strong>After matchweek {latest.as_of_matchweek}</strong>
        </div>
        <span className="section-heading__meta">{updates.length} match observation{updates.length === 1 ? '' : 's'}</span>
      </div>

      <div className="stat-grid posterior-panel__metrics">
        {updatedMetrics.map(([key, metric]) => {
          const display = METRIC_DISPLAY[key] ?? { label: key, unit: '', decimals: 2 };
          const priorMean = prior.continuous_metrics?.[key]?.mean;
          const delta = priorMean == null ? null : metric.mean - priorMean;
          const deltaLabel = delta == null
            ? null
            : `${delta >= 0 ? '+' : ''}${delta.toFixed(display.decimals)} from preseason prior`;
          return (
            <StatTile
              key={key}
              label={display.label}
              value={fmt(metric.mean, display.decimals)}
              unit={display.unit}
              sub={deltaLabel}
            />
          );
        })}
      </div>

      <div className="gameplan-columns posterior-panel__details">
        <div>
          <div className="section-heading">
            <h2 style={{ fontSize: '0.95rem' }}>Updated formation belief</h2>
          </div>
          <div className="card" style={{ padding: '4px 16px' }}>
            <FormationBars formationPrior={latest.formation_prior} />
          </div>
        </div>
        <div>
          <div className="section-heading">
            <h2 style={{ fontSize: '0.95rem' }}>Evidence log</h2>
          </div>
          <ol className="posterior-log">
            {updates.map((update) => (
              <li className="card posterior-log__item" key={`${update.matchweek}-${update.date}`}>
                <div className="posterior-log__header">
                  <strong>MW{update.matchweek} · {update.opponent}</strong>
                  <span className="tabular-nums">{update.result}</span>
                </div>
                <div className="posterior-log__date">{update.date}</div>
                {update.notable_shifts?.length > 0 ? (
                  <ul className="posterior-log__shifts">
                    {update.notable_shifts.map((shift) => <li key={shift}>{shift}</li>)}
                  </ul>
                ) : (
                  <p className="modal-panel__muted">No material tracked-metric shift.</p>
                )}
                {update.sources?.length > 0 && (
                  <div className="posterior-log__sources">
                    Sources:{' '}
                    {update.sources.map((source, index) => (
                      <span key={source.id}>
                        {index > 0 ? ', ' : ''}
                        <a href={source.url} target="_blank" rel="noreferrer">{source.name}</a>
                      </span>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
}

export function GamePlanTab() {
  const { data: prior, error, loading } = useAsync(loadManagerPrior);
  const { data: posteriors } = useAsync(loadPosteriors);
  const { data: players, loading: playersLoading } = useAsync(loadPlayerProfiles);
  const { data: lineupProjection } = useAsync(loadLineupProjection);

  if (loading) return <LoadingState label="Loading manager prior…" />;
  if (error) return <ErrorState error={error} />;
  if (!prior) return <EmptyState>No manager prior data found.</EmptyState>;

  const metrics = Object.entries(prior.continuous_metrics ?? {});

  return (
    <section>
      <div className="section-heading">
        <h2>Game Plan — {prior.manager}'s Tactical Prior</h2>
        <span className="section-heading__meta">from {prior.source_seasons?.length ?? 0} Bournemouth seasons</span>
      </div>

      <div style={{ marginBottom: 32 }}>
        {playersLoading || !players ? (
          <LoadingState label="Projecting lineup…" />
        ) : (
          <PredictedLineup
            players={players}
            formationPrior={prior.formation_prior}
            lineupProjection={lineupProjection}
          />
        )}
      </div>

      <div className="stat-grid" style={{ marginBottom: 28 }}>
        {metrics.map(([key, m]) => {
          const display = METRIC_DISPLAY[key] ?? { label: key, unit: m.unit ?? '', decimals: 2 };
          return (
            <StatTile
              key={key}
              label={display.label}
              value={fmt(m.mean, display.decimals)}
              unit={display.unit}
              sub={m.notes}
            />
          );
        })}
      </div>

      <div className="gameplan-columns">
        <div>
          <div className="section-heading">
            <h2 style={{ fontSize: '0.95rem' }}>Formation prior</h2>
          </div>
          <div className="card" style={{ padding: '4px 16px' }}>
            <FormationBars formationPrior={prior.formation_prior} />
          </div>
          {prior.formation_prior?.notes && <p className="modal-panel__muted" style={{ marginTop: 8 }}>{prior.formation_prior.notes}</p>}
        </div>

        <div>
          <div className="section-heading">
            <h2 style={{ fontSize: '0.95rem' }}>Season xG (Bournemouth)</h2>
          </div>
          <div className="card" style={{ padding: '4px 16px' }}>
            <XgTrend seasonXg={prior.season_xg_totals} />
          </div>
        </div>
      </div>

      {prior.style_notes?.length > 0 && (
        <div style={{ marginTop: 28 }}>
          <div className="section-heading">
            <h2 style={{ fontSize: '0.95rem' }}>Style notes</h2>
          </div>
          <ul className="notes-list card" style={{ padding: '14px 20px' }}>
            {prior.style_notes.map((note, i) => (
              <li key={i}>{note}</li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ marginTop: 28 }}>
        <div className="section-heading">
          <h2 style={{ fontSize: '0.95rem' }}>Posterior (updated from real 2026/27 results)</h2>
        </div>
        <div className="posterior-explainer card">
          <strong>Why this does not update all at once</strong>
          <p>
            The final score can update shortly after full time. Tactical metrics follow after a 24–72 hour
            evidence window while official statistics and trusted analysis are collected, compared, and
            validated. Missing or incompatible measurements stay unchanged rather than being guessed.
          </p>
          <div className="posterior-explainer__flow" aria-label="Posterior update sequence">
            <span>Final result</span><span aria-hidden="true">→</span>
            <span>Evidence review</span><span aria-hidden="true">→</span>
            <span>Validated posterior</span>
          </div>
        </div>
        {posteriors && posteriors.length > 0 ? (
          <PosteriorPanel posteriors={posteriors} prior={prior} />
        ) : (
          <EmptyState>
            No reviewed match observation has produced a posterior yet. Everything above is the preseason prior.
            After a final match is sourced and validated through <code>pipeline/build_posteriors.py</code>, the
            updated belief and its evidence log will appear here.
          </EmptyState>
        )}
      </div>
    </section>
  );
}
