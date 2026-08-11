// In-depth tactical projections for the players predictLineup.js actually
// selects into the most-likely XI. Each entry reasons from three real
// inputs: (1) the player's own sourced skillset/stats (data/player_profiles/),
// (2) Iraola's real tactical signature (data/manager_priors/iraola_2026.json
// -- PPDA 9.45 elite press, 50.5% possession/not dominant, 2.65 accurate
// crosses/match ("through the middle, not width-and-crosses"), direct
// vertical buildup, centre-backs instructed to aggressively step and
// man-mark dropping forwards), and (3) standard 4-2-3-1 zonal geometry.
// The `outlook` field is a hedged, reasoned expectation grounded in real
// trend data where it exists -- never a fabricated specific stat.
//
// If predictLineup.js ever selects a player_id not listed here (a new
// signing, an injury reshuffle), the UI falls back to a generic message
// rather than silently showing nothing -- see PredictedLineup.jsx.
export const ROLE_PROJECTIONS = {
  becker_alisson: {
    headline: 'The outlet when the press gets bypassed',
    zone: 'Sweeper-keeper, operating well off his line behind an elite-press back four.',
    reasoning:
      "Iraola's Bournemouth pressed at an elite 9.45 PPDA -- among the most aggressive in the league both recent seasons -- which pushes the whole defensive line high up the pitch. That leaves a large space in behind that only works if the keeper can sweep it and distribute quickly under pressure. Alisson's long, accurate distribution is exactly the tool that made Liverpool's own high-press system function from 2018 onward.",
    outlook:
      "Expect a more advanced starting position and more first-time long diagonals than a keeper under a deeper, more conservative buildup scheme would need to play.",
  },
  kerkez_milos: {
    headline: 'The one role that needs no translation',
    zone: 'High, overlapping left flank -- functionally an auxiliary winger once Liverpool have the ball in the final third.',
    reasoning:
      "This is the one player in the XI whose fit isn't inferred -- it's observed. Kerkez started all 38 Premier League games at left-back for Iraola's Bournemouth in 2024/25, the exact overlapping, front-foot role this system asks of its full-backs in a direct, vertical attack.",
    outlook:
      "Of anyone in this projected XI, his output should be the most predictable -- not an adaptation to a new idea, just a continuation of a job he already excelled in under this specific manager.",
  },
  vandijk_virgil: {
    headline: 'Elite discipline, redeployed against its instinct',
    zone: 'Still the defensive organizer, but required to step 10-15 yards out of the back line to man-mark forwards dropping into midfield.',
    reasoning:
      "Iraola's centre-backs are explicitly coached to aggressively step out and mark dropping forwards -- a named 'high-risk, high-reward' instruction in the manager's own tactical profile, not a standard positionally-disciplined CB job. Van Dijk's entire reputation is built on elite timing and reading the game from a settled position, which is nearly the opposite skill to repeatedly abandoning the line on a trigger.",
    outlook:
      "Worth watching for real tactical friction here, not a seamless fit -- a defender built on discipline being asked to gamble more than he ever has under previous managers.",
  },
  jacquet_jeremy: {
    headline: 'The same demanding job, with no margin for error',
    zone: 'Same aggressive stepping requirement as Van Dijk, but alongside a partner he has zero shared match minutes with.',
    reasoning:
      "The CB stepping instruction is already the highest-risk job in the defense -- it specifically punishes hesitation or miscommunication, since the space it leaves in behind is only covered if both centre-backs are reading the trigger together. A 21-year-old with a single injury-shortened Ligue 1 season and zero senior Liverpool minutes is about as untested a partner for that specific job as the current squad has.",
    outlook:
      "The most live tactical risk in the projected side -- expect Liverpool to look most exposed in behind specifically through his side of the defense until he settles in or a fit alternative (Gomez, Leoni) returns.",
  },
  frimpong_jeremie: {
    headline: 'An inside passer, not a touchline crosser',
    zone: 'Inverts into central midfield once Liverpool have possession, rather than holding the right touchline.',
    reasoning:
      "Frimpong was frequently deployed as an advanced, inverted wing-back under Xabi Alonso at Leverkusen -- tucking infield to become an auxiliary central passer rather than a conventional overlapping full-back. That maps directly onto Iraola's own service pattern: Bournemouth ranked 17th-19th in the league for crosses both recent seasons, so a right-back who adds passing options centrally is a better fit for how this team actually creates chances than a traditional wide crosser would be.",
    outlook:
      "Expect his influence to show up in central possession and combination play more than in cross counts -- a continuation of the Leverkusen pattern, not a reversion to orthodox full-back play.",
  },
  gravenberch_ryan: {
    headline: 'The pivot licensed to break lines himself',
    zone: 'Deep double-pivot, but with license to carry the ball forward rather than just recycle it sideways.',
    reasoning:
      "His 2025/26 data -- 76 touches/90 and an unusually high 1.14 shots/90 for a holding midfielder -- describes a mobile, ball-carrying #6, not a stationary shield. That matters specifically here: Iraola's own style_notes flag his team as 'one of the weakest in the league at retaining possession under opposition pressure.' A pivot who can dribble out of pressure himself, rather than only recycling under it, directly compensates for a documented team weakness.",
    outlook:
      "Likely the midfielder most trusted to break lines under his own steam when the double pivot is pressed, rather than just the safe out-ball.",
  },
  macallister_alexis: {
    headline: 'The base the carrier plays in front of',
    zone: 'Deeper half of the double pivot, covering the space Gravenberch vacates when he carries forward.',
    reasoning:
      "Reporting on his 2025/26 season already describes a deliberate shift into a deeper, more controlling role compared to his earlier attacking-midfielder profile at Brighton and his first two Liverpool seasons. Paired with a partner (Gravenberch) licensed to drive forward, the standard pivot logic is that one half holds the base -- Mac Allister's own real-world redeployment already points that way independent of this pairing.",
    outlook:
      "Expect his goal/assist numbers to stay modest -- his 2025/26 season produced just 2 goals and 4 assists -- because the job here is protecting the space behind Gravenberch, not arriving in the box himself.",
  },
  gakpo_cody: {
    headline: 'A shooter in a system with no crosses to swing',
    zone: 'Left wing but cuts inside into central, shooting positions rather than staying out on the touchline.',
    reasoning:
      "Gakpo's 2025/26 season (2.85 shots/90, 0.35 xG/90, 87 shots across the campaign) already describes a player who shoots rather than crosses. That fits Iraola's actual service pattern almost exactly: at 2.65 accurate crosses per match, ranked 17th-19th in the league both recent seasons, this team does not create chances by getting to the byline and whipping balls in -- it's build through the middle. A winger who takes the shot himself is a far better system fit than a traditional wide provider.",
    outlook:
      "His shot volume, not his cross count, is the number worth tracking -- crossing metrics would be measuring the wrong thing entirely for this role.",
  },
  wirtz_florian: {
    headline: 'The free man in the pocket, still growing into it',
    zone: "The #10 pocket between the double pivot and the striker -- central, not tied to a flank, receiving between the lines.",
    reasoning:
      "35 goals and 45 assists across 140 Bundesliga appearances at Leverkusen already mark him as a scorer-creator hybrid, not a pure playmaker. His in-season Liverpool data shows real growth into a more involved, more defensively engaged version of that: touches/90 rose from 63.9 to 81.9 and duel-win rate from 36.2% to 45.5% across the season. In a system built on direct, vertical buildup rather than patient wide combination, service into the box comes through central combination and late box-arrivals rather than cutbacks from crosses -- a #10 who already scores as often as he creates arguably fits that pattern better than a pure creator would.",
    outlook:
      "Worth watching whether his shot involvement climbs relative to his assist-heavy Leverkusen split, given this system feeds the box more directly than patient wide buildup ever would.",
  },
  chiesa_federico: {
    headline: 'The same system logic, on almost no evidence',
    zone: 'Mirrors Gakpo on the opposite flank -- theoretically another inside-cutting threat rather than a byline crosser.',
    reasoning:
      "The same 'low crosses, cut inside, shoot' logic that fits Gakpo's real data applies in theory to Chiesa's profile (RW with ST as a secondary position) too. The difference is evidence: Gakpo's inside-cutting tendency shows up directly in his own shot data, while Chiesa's 2025/26 season is a 318-minute sample, heavily used off the bench, nowhere near enough to confirm the same pattern actually holds for him in this team.",
    outlook:
      "The honest read is that this is a projection built on system logic, not on observed Chiesa-specific evidence -- treat it as the most speculative slot in the entire lineup, compounded by his unresolved transfer situation.",
  },
  isak_alexander: {
    headline: 'The finisher a direct system is built to feed',
    zone: 'The point of attack in behind the double pivot -- the target for line-breaking passes, not for crosses into a crowded box.',
    reasoning:
      "23 goals in 34 Premier League games for Newcastle in 2024/25 is elite penalty-box finishing output from a natural in-behind striker, not a target-man or hold-up #9. That's close to the ideal profile for 'direct, vertical attacking buildup' -- a system that isn't trying to work the ball into wide crossing positions is, by construction, trying to find exactly this kind of forward with passes through the middle instead.",
    outlook:
      "On ability alone this is the cleanest system fit in the entire XI -- an elite finisher paired with a team built to feed him directly. The only real question is fitness, given how badly his Liverpool debut season was interrupted, not tactical suitability.",
  },
};

export const GENERIC_ROLE_FALLBACK = {
  headline: 'Role projection not yet written',
  zone: null,
  reasoning:
    "This player wasn't part of the most-likely XI when the role projections were last authored (a squad or injury change since then). The position-estimate basis and confidence above still reflect the current data -- open the full player profile from the Squad & Stats tab for career and playstyle detail.",
  outlook: null,
};
