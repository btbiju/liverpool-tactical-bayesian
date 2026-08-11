// A qualitative "how do they actually play" description for every squad
// player, grounded in the real facts already in their career_stints notes
// and playstyle_metrics (data/player_profiles/) -- not invented. This is
// deliberately separate from the Methodology & data-quality notes section:
// that documents sourcing rigor, this describes football.
export const PLAYING_STYLE = {
  // Goalkeepers
  becker_alisson:
    "One of the defining ball-playing goalkeepers of his generation -- eight seasons and 255+ Premier League appearances established the long, accurate distribution that helped reshape how Liverpool built out from the back from 2018 onward. Still the clear #1 by a wide margin.",
  mamardashvili_giorgi:
    "A commanding, shot-stopping #1 in his final Valencia seasons (2021-2025) before the Liverpool move. His 2025/26 Liverpool season was purely a backup role (10 PL starts, 65.4% save rate, 868 minutes) behind Alisson -- not enough game time to say how his game has adapted to a new league yet.",
  jaros_vitezslav:
    "Still building a first-team track record. His clearest form came on an Ajax loan (19 Eredivisie starts, all 6 Champions League group matches, 5 clean sheets) before a serious knee injury cut the season short -- an emerging shot-stopper, not yet Premier League-tested at senior level.",
  woodman_freddie:
    "A journeyman English #1 -- years of loans at Newcastle before finally nailing down a starting job at Preston North End (2022-2025). Liverpool's third-choice keeper now, with only cameo first-team minutes since arriving.",
  davies_harvey:
    "Still developing outside the first-team picture entirely -- League Two loans at Crewe and Crawley, no senior Liverpool minutes. Too early in his career to characterize a style at this level.",

  // Defenders
  vandijk_virgil:
    "One of the most positionally disciplined, aerially dominant centre-backs in the world -- reads the game to defend from a settled position rather than reacting to it, with genuine passing range to start attacks himself. Still ever-present at 38 Premier League appearances and 3,420 minutes in 2025/26.",
  jacquet_jeremy:
    "Genuinely unproven at this level. A single, injury-shortened Ligue 1 season at Rennes (1,673 minutes) is the entirety of his senior first-team experience -- there isn't yet enough first-team data to describe a settled defensive style, only raw tools and potential.",
  gomez_joseph:
    "Liverpool's longest-serving outfield player (since 2015, 20,254 minutes for the club) -- a versatile, positionally sound defender comfortable at centre-back or right-back. His role has shrunk to squad depth in recent seasons (597 minutes in 2025/26), used in short bursts rather than as a first-choice starter.",
  leoni_giovanni:
    "A genuine breakout at Parma in 2024/25 (Serie A, first goal a header vs Cagliari) built his reputation as a composed, ball-playing young centre-back before the big-money Liverpool move. His entire Liverpool sample is a single minute before an ACL rupture on debut -- his actual level in England is still unobserved.",
  kerkez_milos:
    "A front-foot, overlapping left-back rather than a conservative one -- started all 38 Premier League games under Iraola at Bournemouth in 2024/25, directly informing how this project's manager prior already expects him to be used. Constant runs forward in behind the winger ahead of him.",
  bradley_conor:
    "A converted winger who still carries an attacking instinct into full-back play -- comfortable driving forward and shooting from distance (a solo goal vs Chelsea, Jan 2024). Repeatedly had to fit his development around Trent Alexander-Arnold's presence in the same role, now recovering from a serious knee injury.",
  frimpong_jeremie:
    "An advanced, inverted wing-back at Bayer Leverkusen under Xabi Alonso rather than a conventional stay-at-home full-back -- tucks infield in possession to effectively play as an auxiliary midfielder, and gets forward as a genuine attacking outlet rather than just an overlap option.",
  ramsay_calvin:
    "Won Scotland's Young Player of the Year at Aberdeen in 2021/22, but almost every season since the Liverpool move has been a thin, injury-interrupted loan (Preston, Bolton, Wigan, Kilmarnock) -- real talent that simply hasn't had the sustained minutes to show what his senior game actually looks like.",
  tsimikas_konstantinos:
    "A high-crossing-volume left-back (65 crosses, 15 accurate in his 2025/26 Roma loan alone) built as a service-first, deliver-from-wide profile -- five seasons of rotation behind Andy Robertson at Liverpool, now further down the pecking order since Kerkez's arrival.",

  // Midfielders
  endo_wataru:
    "A defensively disciplined holding midfielder and Japan's national team captain -- positionally responsible rather than expansive. His Liverpool role has shrunk sharply (170 minutes in 2025/26), now firmly a squad-depth option rather than a first-choice #6.",
  wirtz_florian:
    "A genuine creator-and-scorer hybrid #10 -- 35 goals and 45 assists across 140 Bundesliga appearances at Leverkusen is elite dual-threat output, not just a chance-creator. His Liverpool form data shows real in-season adaptation: touches/90 climbed from 63.9 to 81.9 and duel-win rate from 36.2% to 45.5% across the season, a player getting more involved and better at winning the ball back under pressure as the year went on.",
  szoboszlai_dominik:
    "A high-output box-to-box midfielder with a genuine goalscoring and creative threat, not just a defensive presence -- his 2025/26 season (13 goals, 12 assists, 1.98 shots/90) made him Liverpool's second-highest scorer and Players' Player of the Season.",
  macallister_alexis:
    "Broke out at Brighton as an attacking central midfielder, but has been deliberately redeployed into a deeper, more controlling role in his most recent Liverpool season -- a real shift from a goal/assist creator toward a tempo-setting, possession-recycling #6/8 hybrid rather than his earlier attacking profile.",
  jones_curtis:
    "A genuinely versatile Liverpool academy graduate, comfortable across DM/RB/AM/CM. His 2025/26 numbers (1.03 shots/90 across 1,930 minutes) point to a moderate, controlled attacking output rather than either a pure destroyer or a chance-creation focal point.",
  elliott_harvey:
    "A technically gifted prodigy (the youngest player in Premier League history at his 2018/19 debut) who has never quite nailed down a defined role at Liverpool -- his most productive season remains 2023/24, and a 2025/26 loan to Aston Villa (211 minutes) ended without the permanent move Villa's manager wasn't interested in making.",
  gravenberch_ryan:
    "Converted from a more advanced Ajax midfielder into a deeper defensive-midfield screen at Liverpool. His 2025/26 numbers (76 touches/90, 1.14 shots/90) describe a mobile, high-involvement #6 who still carries some of his earlier progressive, forward-carrying instincts rather than a purely destructive holding player.",
  nyoni_trey:
    "An academy prospect with almost no senior minutes -- Liverpool's youngest-ever Champions League player (Jan 2025, aged 17) but genuinely still developing. Not enough first-team sample to describe an established style yet.",
  bajcetic_stefan:
    "Was a breakout defensive-midfield talent in 2022-2024 before a long-term hamstring injury derailed his progress. His loan spells since (Salzburg, Las Palmas) have been thin and interrupted, so his current level and style are genuinely uncertain rather than settled.",

  // Forwards
  isak_alexander:
    "An elite, clinical out-and-out striker -- 23 goals in 34 Premier League games for Newcastle in 2024/25 is top-of-the-league production, built on being a natural penalty-box finisher rather than a build-up or link forward. His Liverpool sample so far has been badly interrupted by fitness issues, so that level hasn't yet been seen in Liverpool colours.",
  chiesa_federico:
    "A direct, pacey wide forward comfortable on either flank or centrally (RW/ST) -- but his Liverpool tenure has been defined by a bench-heavy role (41 of 50 appearances as a substitute) rather than settled game time to actually show that profile, and he's currently in the middle of an unresolved transfer situation.",
  gakpo_cody:
    "A cutting-inside, shooting wide forward rather than a provider who lives on crosses -- his 2025/26 season (2.85 shots/90, 0.35 xG/90, 87 shots across the campaign) is genuine high-volume goal-threat output from the left, not primarily a service role.",
  munoz_victor:
    "A fresh, direct breakout winger off a single standout Osasuna season (7 goals, 5 assists across 2,668 minutes in 2025/26) -- genuinely new to this level of football, with zero Liverpool minutes yet to show how that translates to the Premier League.",
  ngumoha_rio:
    "An explosive teenage dribbler and Liverpool's youngest-ever starter -- his 2025/26 breakthrough (952 minutes, 2 goals) already gave him more first-team minutes than most Premier League players his age get anywhere. Still a genuinely new, high-ceiling talent rather than a finished product.",
  ekitike_hugo:
    "A career-best 2024/25 season at Frankfurt (15 Bundesliga goals, 12 assists) established a real goal-and-creation dual-threat centre-forward profile before his big Liverpool move. His 2025/26 Liverpool numbers (3.23 shots/90, 0.56 xG/90 across 1,810 minutes) point to an even higher shot-volume, high-xG version of that -- before a ruptured Achilles ended his season early.",
};
