// Projects a most-likely starting XI from real squad data: the manager's
// dominant formation (formation_prior), each player's position_estimate
// (primary/secondary/confidence), and current injury_status. This is a
// model projection, not reported team news -- see PredictedLineup.jsx for
// how it's labeled in the UI.

// Only 4-2-3-1 has a visualized layout -- it's the dominant formation by a
// wide margin (see data/manager_priors/iraola_2026.json formation_prior).
export const SUPPORTED_FORMATION = '4-2-3-1';

// x/y are percentages of the pitch, y=0 at the opponent's goal (top), y=100
// at Liverpool's own goal (bottom) -- matches how the pitch SVG is drawn.
const SLOTS_4_2_3_1 = [
  { id: 'GK', code: 'GK', label: 'Goalkeeper', x: 50, y: 92 },
  { id: 'LB', code: 'LB', label: 'Left-back', x: 14, y: 72 },
  { id: 'CB1', code: 'CB', label: 'Centre-back', x: 36, y: 78 },
  { id: 'CB2', code: 'CB', label: 'Centre-back', x: 64, y: 78 },
  { id: 'RB', code: 'RB', label: 'Right-back', x: 86, y: 72 },
  { id: 'DM1', code: 'DM', label: 'Defensive midfield', x: 35, y: 54 },
  { id: 'DM2', code: 'DM', label: 'Defensive midfield', x: 65, y: 54 },
  { id: 'LW', code: 'LW', label: 'Left wing', x: 15, y: 28 },
  { id: 'AM', code: 'AM', label: 'Attacking midfield', x: 50, y: 30 },
  { id: 'RW', code: 'RW', label: 'Right wing', x: 85, y: 28 },
  { id: 'ST', code: 'ST', label: 'Striker', x: 50, y: 8 },
];

// Positions accepted for each slot, most-natural first (used as a scoring
// tiebreak only; primary/secondary match already dominates the score).
const SLOT_MATCH = {
  GK: ['GK'],
  LB: ['LB', 'LWB', 'LM'],
  CB: ['CB'],
  RB: ['RB', 'RWB', 'RM'],
  DM: ['DM', 'CM'],
  AM: ['AM', 'CM'],
  LW: ['LW', 'LM'],
  RW: ['RW', 'RM'],
  ST: ['ST'],
};

// Broad group per position code, used only as a last-resort fallback so a
// slot is never left empty just because no exact/near match is fit.
const GROUP_OF = {
  GK: 'GK',
  CB: 'DEF', RB: 'DEF', LB: 'DEF', RWB: 'DEF', LWB: 'DEF',
  DM: 'MID', CM: 'MID', AM: 'MID', RM: 'MID', LM: 'MID',
  RW: 'FWD', LW: 'FWD', ST: 'FWD',
};

function scoreCandidate(player, slotCode) {
  const primary = player.position_estimate?.primary;
  const secondary = player.position_estimate?.secondary;
  const acceptable = SLOT_MATCH[slotCode];
  if (primary && acceptable.includes(primary)) return primary === slotCode ? 3 : 2;
  if (secondary && acceptable.includes(secondary)) return 1;
  if (primary && GROUP_OF[primary] === GROUP_OF[slotCode]) return 0.5;
  return -1;
}

export function predictLineup(players) {
  const pool = players.filter((p) => !p.injury_status);
  const used = new Set();
  const slots = SLOTS_4_2_3_1.map((slot) => {
    const scored = pool
      .filter((p) => !used.has(p.player_id))
      .map((p) => ({ player: p, score: scoreCandidate(p, slot.code) }))
      .filter((x) => x.score >= 0)
      .sort((a, b) => b.score - a.score || (b.player.position_estimate?.confidence ?? 0) - (a.player.position_estimate?.confidence ?? 0));

    const best = scored[0] ?? null;
    if (best) used.add(best.player.player_id);

    return {
      ...slot,
      player: best?.player ?? null,
      isNaturalFit: best ? best.score >= 1 : false,
    };
  });

  return { formation: SUPPORTED_FORMATION, slots };
}
