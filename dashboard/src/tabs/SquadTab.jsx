import { useMemo, useState } from 'react';
import { useAsync } from '../hooks/useAsync.js';
import { loadPlayerProfiles } from '../lib/dataLoaders.js';
import { LoadingState, ErrorState, EmptyState } from '../components/StatusStates.jsx';
import { GROUP_ACCENT, GROUP_ORDER, positionGroup } from '../lib/positions.js';
import { PlayerCard } from './PlayerCard.jsx';
import { PlayerDetail } from './PlayerDetail.jsx';

export function SquadTab() {
  const { data: players, error, loading } = useAsync(loadPlayerProfiles);
  const [activeGroup, setActiveGroup] = useState('All');
  const [selectedId, setSelectedId] = useState(null);

  const grouped = useMemo(() => {
    if (!players) return {};
    const byGroup = {};
    for (const p of players) {
      const g = positionGroup(p.position_estimate?.primary);
      (byGroup[g] ??= []).push(p);
    }
    for (const g of Object.keys(byGroup)) {
      byGroup[g].sort((a, b) => (a.current_squad_number ?? 999) - (b.current_squad_number ?? 999));
    }
    return byGroup;
  }, [players]);

  if (loading) return <LoadingState label="Loading squad…" />;
  if (error) return <ErrorState error={error} />;
  if (!players || players.length === 0) {
    return <EmptyState>No player profiles found in data/player_profiles/.</EmptyState>;
  }

  const groupsToShow = activeGroup === 'All' ? GROUP_ORDER : [activeGroup];
  const selectedPlayer = players.find((p) => p.player_id === selectedId) ?? null;

  return (
    <section>
      <div className="section-heading">
        <h2>Squad &amp; Player Stats</h2>
        <span className="section-heading__meta">{players.length} players</span>
      </div>

      <div className="filter-chips" role="tablist" aria-label="Filter by position">
        <button
          type="button"
          className={`filter-chip${activeGroup === 'All' ? ' filter-chip--active' : ''}`}
          onClick={() => setActiveGroup('All')}
        >
          All
        </button>
        {GROUP_ORDER.map((g) => (
          <button
            key={g}
            type="button"
            className={`filter-chip${activeGroup === g ? ' filter-chip--active' : ''}`}
            style={{ '--chip-accent': `var(${GROUP_ACCENT[g]})` }}
            onClick={() => setActiveGroup(g)}
          >
            {g}
          </button>
        ))}
      </div>

      {groupsToShow.map((g) =>
        grouped[g]?.length ? (
          <div key={g} className="player-group">
            {activeGroup === 'All' && <h3 className="player-group__heading">{g}</h3>}
            <div className="player-grid">
              {grouped[g].map((p) => (
                <PlayerCard key={p.player_id} player={p} onOpen={setSelectedId} />
              ))}
            </div>
          </div>
        ) : null
      )}

      <PlayerDetail player={selectedPlayer} onClose={() => setSelectedId(null)} />
    </section>
  );
}
