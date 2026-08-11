import { useEffect } from 'react';
import { Badge } from '../components/Badge.jsx';
import { splitNotesAndSources } from '../lib/parseSources.js';

const METRIC_LABELS = {
  minutes: 'Minutes',
  shots_per90: 'Shots /90',
  xg_per90: 'xG /90',
  pass_accuracy_pct: 'Pass accuracy %',
  progressive_passes_per90: 'Progressive passes /90',
  touches_per90: 'Touches /90',
  duels_won_pct: 'Duels won %',
};

const BASIS_LABELS = {
  liverpool_recent_minutes: 'Recent Liverpool minutes',
  prior_club_recent_minutes: "Recent prior-club minutes (Liverpool sample too thin)",
  manager_overlay_adjusted: 'Manager overlay (insufficient individual data)',
  in_season_observed: '2026/27 in-season observation',
};

export function PlayerDetail({ player, onClose, roleProjection, slotLabel }) {
  useEffect(() => {
    function onKey(e) {
      if (e.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  if (!player) return null;

  const pm = player.playstyle_metrics ?? {};
  const populatedMetrics = Object.entries(pm).filter(([k, v]) => k !== 'source_season' && k !== 'source_club' && v != null);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-panel"
        role="dialog"
        aria-modal="true"
        aria-label={player.name}
        onClick={(e) => e.stopPropagation()}
      >
        <button type="button" className="modal-panel__close" onClick={onClose} aria-label="Close">
          ×
        </button>

        <div className="modal-panel__header">
          <span className="player-card__number tabular-nums modal-panel__number">
            {player.current_squad_number ?? '—'}
          </span>
          <div>
            <h2>{player.name}</h2>
            <p className="modal-panel__subtitle">
              {slotLabel ?? player.position_estimate?.primary}
              {!slotLabel && player.position_estimate?.secondary ? ` / ${player.position_estimate.secondary}` : ''}
            </p>
          </div>
        </div>

        <div className="modal-panel__badges">
          {player.injury_status ? <Badge tone="serious">Injured</Badge> : <Badge tone="good">Available</Badge>}
          {!player.has_liverpool_minutes && <Badge tone="neutral">No Liverpool history</Badge>}
          <Badge tone="neutral">Confidence {Math.round((player.position_estimate?.confidence ?? 0) * 100)}%</Badge>
        </div>

        {roleProjection && (
          <section className="modal-panel__section modal-panel__section--role">
            <h3>Projected role under Iraola</h3>
            <p className="role-projection__headline">{roleProjection.headline}</p>
            <p>{roleProjection.role}</p>
            <p className="modal-panel__muted">
              Model projection synthesized from this player's real career data and Iraola's tactical prior — not
              confirmed team news.
            </p>
          </section>
        )}

        {player.injury_status && (
          <section className="modal-panel__section">
            <h3>Injury</h3>
            <p>{player.injury_status.description}</p>
            {player.injury_status.expected_return && (
              <p className="modal-panel__muted">Expected return: {player.injury_status.expected_return}</p>
            )}
          </section>
        )}

        <section className="modal-panel__section">
          <h3>Position estimate basis</h3>
          <p>{BASIS_LABELS[player.position_estimate?.basis] ?? player.position_estimate?.basis}</p>
        </section>

        <section className="modal-panel__section">
          <h3>Career</h3>
          <table className="stints-table">
            <thead>
              <tr>
                <th>Club</th>
                <th>Period</th>
                <th>Apps</th>
                <th>Goals</th>
                <th>Assists</th>
              </tr>
            </thead>
            <tbody>
              {(player.career_stints ?? []).map((stint, i) => (
                <tr key={`${stint.club}-${i}`}>
                  <td>{stint.club}</td>
                  <td>{stint.period}</td>
                  <td className="tabular-nums">{stint.appearances ?? '—'}</td>
                  <td className="tabular-nums">{stint.goals ?? '—'}</td>
                  <td className="tabular-nums">{stint.assists ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {populatedMetrics.length > 0 && (
          <section className="modal-panel__section">
            <h3>
              Playstyle metrics
              {pm.source_club ? (
                <span className="modal-panel__muted"> — {pm.source_season} at {pm.source_club}</span>
              ) : null}
            </h3>
            <dl className="metric-list">
              {populatedMetrics.map(([key, value]) => (
                <div key={key} className="metric-list__row">
                  <dt>{METRIC_LABELS[key] ?? key}</dt>
                  <dd className="tabular-nums">{value}</dd>
                </div>
              ))}
            </dl>
          </section>
        )}

        {player.notes?.length > 0 &&
          (() => {
            const { notes: methodNotes, sources } = splitNotesAndSources(player.notes);
            return (
              <>
                {methodNotes.length > 0 && (
                  <section className="modal-panel__section">
                    <h3>Methodology &amp; data-quality notes</h3>
                    <ul className="notes-list">
                      {methodNotes.map((note, i) => (
                        <li key={i}>{note}</li>
                      ))}
                    </ul>
                  </section>
                )}
                {sources && (
                  <section className="modal-panel__section">
                    <h3>Sources{sources.via ? <span className="modal-panel__muted"> — {sources.via}</span> : null}</h3>
                    <table className="sources-table">
                      <tbody>
                        {sources.entries.map((s, i) => (
                          <tr key={i}>
                            <td className="sources-table__name">{s.name}</td>
                            <td className="sources-table__context">{s.context ?? ''}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </section>
                )}
              </>
            );
          })()}
      </div>
    </div>
  );
}
