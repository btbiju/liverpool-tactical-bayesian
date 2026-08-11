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

export function PredictedLineup({ players, formationPrior }) {
  const [openSlot, setOpenSlot] = useState(null);
  const { formation, slots } = predictLineup(players);

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
          Projected XI — {formation}{' '}
          <span className="modal-panel__muted" style={{ fontWeight: 400 }}>({likelihood}% likely formation)</span>
        </h2>
      </div>
      <p className="lineup-disclaimer">
        A model projection from current squad data — most-likely formation, each player's estimated position and
        confidence, and who's currently injured. <strong>Not confirmed team news.</strong> Click any player for their
        projected role. Dashed markers are out-of-position fallback picks forced by injuries elsewhere in the squad.
      </p>

      <div className="pitch">
        <div className="pitch__halfway-line" />
        <div className="pitch__center-circle" />
        <div className="pitch__box pitch__box--top" />
        <div className="pitch__box pitch__box--bottom" />
        {slots.map((slot) => (
          <PitchMarker key={slot.id} slot={slot} onOpen={setOpenSlot} />
        ))}
      </div>

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
