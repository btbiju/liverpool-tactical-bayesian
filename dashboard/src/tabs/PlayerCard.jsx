import { Badge } from '../components/Badge.jsx';
import { GROUP_ACCENT, positionGroup } from '../lib/positions.js';

export function PlayerCard({ player, onOpen }) {
  const group = positionGroup(player.position_estimate?.primary);
  const accentVar = GROUP_ACCENT[group];
  const injured = Boolean(player.injury_status);

  return (
    <button
      type="button"
      className="player-card"
      style={accentVar ? { '--tile-accent': `var(${accentVar})` } : undefined}
      onClick={() => onOpen(player.player_id)}
      aria-label={`${player.name}, ${player.position_estimate?.primary ?? 'position unknown'}${injured ? ', injured' : ''} — view profile`}
    >
      <div className="player-card__top">
        <span className="player-card__number tabular-nums">
          {player.current_squad_number ?? '—'}
        </span>
        <span className="player-card__position">{player.position_estimate?.primary ?? '?'}</span>
      </div>
      <div className="player-card__name">{player.name}</div>
      <div className="player-card__badges">
        {injured ? <Badge tone="serious">Injured</Badge> : null}
        {!player.has_liverpool_minutes ? <Badge tone="neutral">No LFC history</Badge> : null}
      </div>
    </button>
  );
}
