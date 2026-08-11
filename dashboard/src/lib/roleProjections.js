// Hand-written role projections for the players the predictLineup.js
// algorithm actually selects into the most-likely XI. Grounded in each
// player's real profile data (data/player_profiles/) and Iraola's real
// tactical prior (data/manager_priors/iraola_2026.json) -- not fabricated,
// but explicitly a synthesized projection, not reported team news. Flagged
// clearly in the UI (see PredictedLineup.jsx).
//
// If predictLineup.js ever selects a player_id not listed here (a new
// signing, an injury reshuffle), the UI falls back to a generic message
// rather than silently showing nothing -- see PredictedLineup.jsx.
export const ROLE_PROJECTIONS = {
  becker_alisson: {
    headline: 'The last line of an extreme press',
    role: "Alisson has been Liverpool's undisputed #1 since 2018 and remains it here (95% confidence) over Mamardashvili's backup role. Iraola's Bournemouth sides pressed at an elite 9.45 PPDA -- among the most aggressive in the league both recent seasons -- which pushes the defensive line high and leans on a keeper comfortable sweeping behind it and playing out under pressure. That's a long-standing strength of Alisson's game, not a new ask.",
  },
  kerkez_milos: {
    headline: 'Already knows this manager',
    role: "The one player in this XI with a direct, first-hand relationship with Iraola: Kerkez started all 38 Premier League games at left-back for Iraola's Bournemouth in 2024/25 before both moved to Liverpool. Iraola's system wants front-foot, overlapping full-backs supporting a direct, vertical attack rather than sitting deep -- exactly the role Kerkez was already playing under this manager a year ago.",
  },
  vandijk_virgil: {
    headline: 'A different kind of responsibility',
    role: "Liverpool's captain and an ever-present at centre-back (38 PL appearances, 3,420 minutes in 2025/26) is the clearest name on the team sheet. But Iraola's centre-backs are coached to aggressively step out and man-mark dropping forwards -- a high-risk, high-reward instruction that trades defensive shape for pressure, and leaves space in behind when it doesn't come off. That's a real adaptation for a defender built on positional discipline, not just a continuation of his Liverpool role under previous managers.",
  },
  jacquet_jeremy: {
    headline: "The gap this XI can't hide",
    role: "This slot is the honest weak point of the projected lineup, not a vote of confidence. With Joseph Gomez and Giovanni Leoni both injured, the only fit alternative next to Van Dijk is a 21-year-old with zero senior Liverpool minutes, a first Ligue 1 season at Rennes that was itself cut short by a shoulder injury, and the lowest position-estimate confidence (55%) of any starter in this XI. He's selected by elimination, not merit -- worth watching closely once Gomez or Leoni return.",
  },
  frimpong_jeremie: {
    headline: 'An inverted wing-back, redeployed',
    role: "Frimpong spent four and a half seasons at Bayer Leverkusen frequently used as an advanced, inverted wing-back rather than a conventional right-back -- attacking-minded, comfortable high up the pitch. That profile lines up naturally with Iraola's front-foot, direct approach. His debut Liverpool season was interrupted by missing roughly 20 games, which is reflected in a moderate 60% confidence rather than a clear-cut certainty.",
  },
  gravenberch_ryan: {
    headline: 'The press-resistant pivot',
    role: "Gravenberch's 2025/26 data (76 touches/90, a live 1.14 shots/90 for a deep midfielder) points to a mobile, ball-carrying #6 comfortable receiving under pressure -- which matters given Bournemouth-under-Iraola's own style_notes flag them as 'one of the weakest teams in the league at retaining possession under opposition pressure.' At 80% confidence, this is the most secure midfield slot in the projected XI outside the back line.",
  },
  macallister_alexis: {
    headline: 'Pushed deeper, by design',
    role: "Reporting on Mac Allister's 2025/26 season describes a deliberate shift into a deeper, more controlling midfield role compared to his first two Liverpool seasons -- which fits neatly alongside Gravenberch in Iraola's double pivot ahead of the back four. A proven Premier League and World Cup-winning midfielder, already with a domestic cup in Liverpool colours.",
  },
  gakpo_cody: {
    headline: 'A shooter, not a crosser',
    role: "Gakpo's 2025/26 numbers (2.85 shots/90, 0.35 xG/90) describe a player who cuts inside and shoots rather than one who lives out wide crossing into the box -- which matches Iraola's team identity almost exactly: Bournemouth ranked 17th-19th in the league for crosses both recent seasons, described in the manager's own prior as playing 'through the middle, not width-and-crosses.' A stylistically clean fit for the left-wing role in this system.",
  },
  wirtz_florian: {
    headline: 'Still finding his level',
    role: "The marquee #10 signing, but the honest read of his debut Liverpool season is a player still adapting: Opta's own form split shows real in-season improvement (touches/90 rising from 63.9 to 81.9, duel success from 36.2% to 45.5% across his first 20 vs. last 12 games), not immediate world-class certainty. That trajectory, not the reputation alone, is why he holds this slot at a moderate 70% confidence.",
  },
  chiesa_federico: {
    headline: 'The most fragile projection in the XI',
    role: "Chiesa is selected here mainly because no other specialist right winger exists on the fit roster -- not because the underlying data supports it strongly. His 2025/26 season is a thin 318-minute sample, heavily used off the bench, and as of this data he's reported in an active, unresolved transfer saga that could see him leave Liverpool before this projected XI ever takes the pitch. Lowest confidence of any starter (50%).",
  },
  isak_alexander: {
    headline: "Undisputed on ability, uncertain on fitness",
    role: "On pure output there's no competition for the striker slot -- 23 goals in 34 Premier League games for Newcastle in 2024/25 is elite production. But his British-record-fee Liverpool debut season was badly interrupted (just 14 appearances, 702 minutes), and the most recent research pass still found his status flagged 'Injured.' The ability that earns him this slot and the fitness question that shadows it are both real at the same time.",
  },
};

export const GENERIC_ROLE_FALLBACK = {
  headline: 'Role projection not yet written',
  role: "This player wasn't part of the most-likely XI when the role projections were last authored (a squad or injury change since then). The position-estimate basis and confidence above still reflect the current data -- open the full player profile from the Squad & Stats tab for career and playstyle detail.",
};
