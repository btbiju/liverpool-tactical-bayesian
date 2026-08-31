import { useState } from 'react';
import { predictLineup } from '../lib/predictLineup.js';
import { ROLE_PROJECTIONS, GENERIC_ROLE_FALLBACK } from '../lib/roleProjections.js';
import { GROUP_ACCENT, positionGroup } from '../lib/positions.js';
import { shortSurname } from '../lib/displayName.js';
import { PlayerDetail } from './PlayerDetail.jsx';

function PitchMarker({ slot, onOpen }) {
  const player = slot.player;
  const accentVar = player ? GROUP_ACCENT[positionGroup(player.position_estimate?.primary ?? slot.code)] : null;

  return (
    <button
      type="button"
      className="pitch-marker"
      style={{ left: `${slot.x}%`, top: `${slot.y}%`, '--marker-accent': accentVar ? `var(${accentVar})` : 'var(--text-muted)' }}
      onClick={() => player && onOpen(slot)}
      disabled={!player}
      aria-label={player ? `${player.name}, ${slot.label}${slot.isNaturalFit ? '' : ', out-of-position fallback'} — view projected role` : `${slot.label}, no fit candidate available`}
    >
      <span className="pitch-marker__dot tabular-nums">{player?.current_squad_number ?? '—'}</span>
      <span className="pitch-marker__name">{player ? shortSurname(player.name) : '—'}</span>
      {player && !slot.isNaturalFit && <span className="pitch-marker__flag" title="Out-of-position fallback pick" />}
    </button>
  );
}

function MatchPreview({ projection }) {
  const match = projection?.upcoming_match;
  const prediction = projection?.prediction;
  if (!match || !prediction) return null;

  const kickoff = new Intl.DateTimeFormat('en-GB', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  }).format(new Date(match.kickoff));

  const scorerGroups = prediction.goal_scorers.reduce((groups, scorer) => {
    if (!groups[scorer.team]) groups[scorer.team] = [];
    groups[scorer.team].push(scorer);
    return groups;
  }, {});

  return (
    <div className="match-preview card">
      <div className="match-preview__fixture">
        <div>
          <span className="posterior-panel__eyebrow">Next opponent · MW{match.matchweek}</span>
          <strong>Liverpool {match.home_away === 'A' ? 'at' : 'vs'} {match.opponent}</strong>
          <span>{kickoff} · {match.venue}</span>
        </div>
        <div className="match-preview__score">
          <span>Predicted score</span>
          <strong className="tabular-nums">{prediction.display_score}</strong>
          <span>{prediction.confidence} confidence</span>
        </div>
      </div>

      <div className="match-preview__body">
        <div>
          <h3>Predicted scorers</h3>
          {Object.entries(scorerGroups).map(([team, scorers]) => (
            <div className="match-preview__scorer-group" key={team}>
              <strong>{team}</strong>
              <ul>
                {scorers.map((scorer) => (
                  <li key={`${team}-${scorer.player_name}`}>
                    <span>{scorer.player_name}{scorer.goals > 1 ? ` ×${scorer.goals}` : ''}</span>
                    <small>{scorer.reasoning}</small>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div>
          <h3>Why this score</h3>
          <ul className="match-preview__reasoning">
            {prediction.reasoning.map((reason) => <li key={reason}>{reason}</li>)}
          </ul>
        </div>
      </div>
    </div>
  );
}

function MatchupPlan({ projection }) {
  const analysis = projection?.opponent_analysis ?? [];
  const decisions = projection?.selection_reasoning ?? [];
  if (analysis.length === 0 && decisions.length === 0) return null;

  return (
    <div className="matchup-plan">
      <div>
        <div className="section-heading"><h2 style={{ fontSize: '0.95rem' }}>How the opponent plays</h2></div>
        <div className="matchup-plan__stack">
          {analysis.map((item) => (
            <article className="card matchup-plan__item" key={item.label}>
              <h3>{item.label}</h3>
              <p>{item.finding}</p>
              <p><strong>Liverpool response:</strong> {item.matchup_implication}</p>
            </article>
          ))}
        </div>
      </div>
      <div>
        <div className="section-heading"><h2 style={{ fontSize: '0.95rem' }}>Why this XI</h2></div>
        <div className="matchup-plan__stack">
          {decisions.map((item) => (
            <article className="card matchup-plan__item" key={item.label}>
              <h3>{item.label}</h3>
              <p>{item.reasoning}</p>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}

export function PredictedLineup({ players, formationPrior, lineupProjection }) {
  const [openSlot, setOpenSlot] = useState(null);
  const { formation, slots } = predictLineup(players, lineupProjection);

  const alpha = formationPrior?.alpha ?? {};
  const total = Object.values(alpha).reduce((sum, v) => sum + v, 0) || 1;
  const likelihood = Math.round(((alpha[formation] ?? 0) / total) * 100);

  const selectedPlayer = openSlot?.player ?? null;
  const roleProjection = selectedPlayer
    ? ROLE_PROJECTIONS[selectedPlayer.player_id] ?? GENERIC_ROLE_FALLBACK
    : null;

  return (
    <div>
      <div className="section-heading">
        <h2 style={{ fontSize: '0.95rem' }}>
          Projected XI{lineupProjection?.upcoming_match?.opponent ? ` vs ${lineupProjection.upcoming_match.opponent}` : ''} — {formation}{' '}
          <span className="modal-panel__muted" style={{ fontWeight: 400 }}>({likelihood}% likely formation)</span>
        </h2>
      </div>
      <p className="lineup-disclaimer">
        An opponent-specific projection from Iraola's recent selections, current availability, the next opponent's
        structure, and each player's sourced profile. <strong>Not confirmed team news or betting advice.</strong> Click
        any player for their projected role. Dashed markers are out-of-position fallback picks forced by injuries.
      </p>

      <MatchPreview projection={lineupProjection} />

      <div className="pitch">
        <div className="pitch__halfway-line" />
        <div className="pitch__center-circle" />
        <div className="pitch__box pitch__box--top" />
        <div className="pitch__box pitch__box--bottom" />
        {slots.map((slot) => (
          <PitchMarker key={slot.id} slot={slot} onOpen={setOpenSlot} />
        ))}
      </div>

      <MatchupPlan projection={lineupProjection} />

      {openSlot && selectedPlayer && (
        <PlayerDetail
          player={selectedPlayer}
          roleProjection={roleProjection}
          slotLabel={openSlot.label}
          onClose={() => setOpenSlot(null)}
        />
      )}
    </div>
  );
}

export function GamePlanEvidence({ lineupProjection }) {
  if (!lineupProjection) return null;

  const referencedSources = lineupProjection.sources ?? [];

  return (
    <div className="gameplan-evidence">
      <div className="section-heading">
        <h2 style={{ fontSize: '0.95rem' }}>Game-plan evidence and sources</h2>
        <span className="section-heading__meta">Updated {lineupProjection.as_of}</span>
      </div>
      <div className="gameplan-columns">
        <div className="card gameplan-evidence__panel">
          <h3>Observed Liverpool selections</h3>
          <ol>
            {(lineupProjection.evidence ?? []).map((item) => (
              <li key={`${item.date}-${item.opponent}`}>
                <strong>{item.date} · {item.opponent}</strong>
                <span>{item.competition}</span>
                {item.notes && <p>{item.notes}</p>}
              </li>
            ))}
          </ol>
        </div>
        <div className="card gameplan-evidence__panel">
          <h3>Source register</h3>
          <ul>
            {referencedSources.map((source) => (
              <li key={source.id}>
                <a href={source.url} target="_blank" rel="noreferrer">{source.name}</a>
                {source.notes && <p>{source.notes}</p>}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
