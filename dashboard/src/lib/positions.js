const GROUPS = {
  GK: 'Goalkeepers',
  CB: 'Defenders',
  RB: 'Defenders',
  LB: 'Defenders',
  RWB: 'Defenders',
  LWB: 'Defenders',
  DM: 'Midfielders',
  CM: 'Midfielders',
  AM: 'Midfielders',
  RM: 'Midfielders',
  LM: 'Midfielders',
  RW: 'Forwards',
  LW: 'Forwards',
  ST: 'Forwards',
};

export const GROUP_ORDER = ['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards'];

export const GROUP_ACCENT = {
  Goalkeepers: '--series-1',
  Defenders: '--series-2',
  Midfielders: '--series-3',
  Forwards: '--series-4',
};

export function positionGroup(positionCode) {
  return GROUPS[positionCode] ?? 'Other';
}
