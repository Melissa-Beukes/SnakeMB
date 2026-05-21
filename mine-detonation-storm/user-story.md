# User Story: Mine Detonation Storm

================================================================================
USER STORY — MINE DETONATION STORM
Feature ID  : MDS-001
File        : snake_game/User_Story_mine-detonation-storm.txt
Date Created: 2026-03-06
Status      : DRAFT — Awaiting Implementation
Last Amended: 2026-03-06 — Added pre-detonation warning flash phase (AC-3b, AC-4)
================================================================================

FEATURE OVERVIEW

Feature Name : Mine Detonation Storm
Feature Folder: snake_game/mine-detonation-storm/
Depends On   : Flashing Mines feature (snake_game/flashing-mines/) — must be present and functional in all 4 versions before this feature is implemented.

Summary:
  When the active mine count on the grid reaches 10 or more mines, a Mine Detonation Storm event is triggered. During the storm, a flashing red/black border appears around the game window, and mines begin detonating one by one in a random order. Before each mine explodes, it enters a 3-second warning phase in which it flashes rapidly using the explosion colour palette, giving the player time to react and move clear. After the 3-second warning, the explosion sequence begins: the mine's 3x3 grid area erupts with the same flickering explosion colours for 1 second. Each detonation creates one extra food item at the mine's centre cell and kills the snake if it occupies any cell within the 3x3 explosion area during the 1-second explosion. The storm ends once all mines have been detonated. Normal mine creation mechanics (spawning new mines on food-eat events) continue to operate throughout the storm uninterrupted.

USER STORY STATEMENT

As a player of the Snake Game,
When 10 or more mines are simultaneously present on the grid,
I want a Mine Detonation Storm event to trigger,
So that the mines are dramatically cleared through explosions, I receive bonus food for each mine detonated, I have time to react and move clear of each upcoming explosion, and my snake can be killed by explosion blast areas — creating a tense, high-stakes moment in gameplay.

ACCEPTANCE CRITERIA

AC-1 : STORM TRIGGER CONDITION
  a. Triggers when active mine count reaches exactly 10.
  b. Evaluated on each food-eat event that causes mine count to reach 10.
  c. Does not trigger again until current storm fully ends AND mine count reaches 10 again.
  d. Only one storm active at any time.

AC-2 : BORDER FLASH EFFECT
  a. Thin solid-line border drawn along inner edge of game window on all four sides.
  b. Flashes alternately between BRIGHT RED and BLACK at 0.2s interval.
  c. Drawn above background/grid but below game entities.
  d. Independent of mine flash state/timing.
  e. Continues for entire storm duration; stops immediately on storm end.
  f. Console: display '*** DETONATION STORM ***' in bright red ANSI instead.

AC-3 : MINE DETONATION SEQUENCE
  a. Mines detonate one by one in random order.
  b. Each mine has two consecutive phases:
     Phase 1 — WARNING (3 seconds): Mine's single cell flashes using EXPLOSION_COLORS palette at 0.2s interval. No 3x3 effect yet. Snake NOT killed — normal mine collision rules apply (shrink 3, score -3). Mine removed from active mines list at Phase 1 start.
     Phase 2 — EXPLOSION (1 second): 3x3 explosion area active. Snake-kill check applies. Bonus food spawns at Phase 2 start.
  c. Sequence per mine: [WARNING: 3s] → [EXPLOSION: 1s] → [next mine WARNING: 3s] → ... Total per-mine cycle: 4 seconds.
  d. Detonation order shuffled once at storm start.
  e. Storm ends immediately if queue empties.
  f. Only current warning mine uses explosion-palette flash; all others use standard red/grey flash.

AC-4 : EXPLOSION VISUAL EFFECT
  Phase 1 — WARNING FLASH (3s, single cell): Cell flashes random EXPLOSION_COLORS at 0.2s. Console: '!' in bright yellow ANSI.
  Phase 2 — EXPLOSION (1s, 3x3 area): 3x3 cells (clipped at boundary) flicker independently with random colours from palette each render frame. Palette: bright red (255,0,0), orange (255,136,0), yellow (255,255,0), white (255,255,255), bright orange-red (255,68,0). Console: '*' in bright yellow for 1 game tick.

AC-5 : SNAKE KILL ON EXPLOSION
  a. Snake head in any Phase 2 3x3 cell → immediate game over.
  b. Phase 1: no explosion kill — normal mine-hit rules apply.
  c. Head only — body segments do NOT cause death.
  d. Kill check every game tick during Phase 2.
  e. Snake death from Phase 2 → storm ends immediately.

AC-6 : BONUS FOOD ON DETONATION
  a. One extra GREEN food item spawns at mine's centre cell at Phase 2 start.
  b. Multiple food items may coexist during storm.
  c. GREEN (0,255,0)/#00FF00 only — mandatory.
  d. Eating bonus food: score+1, grow, cycle colour.
  e. Bonus food persists after storm; consumed by standard mechanics.
  f. Bonus food placed at centre cell even if occupied by snake body.

AC-7 : STORM END CONDITIONS
  a. Storm ends when detonation queue empty and no phase in progress.
  b. Storm ends immediately if snake dies during Phase 2.
  c. On end: border flash stops, warning/explosion clears, queue cleared, all phase state reset.
  d. Normal mine spawning resumes after storm.

AC-8 : MINE SPAWNING DURING STORM
  a. Normal mine creation continues during storm.
  b. Mines spawned during storm NOT added to current storm queue.
  c. Storm trigger not re-evaluated during active storm — no nested storms.

AC-9 : RESTART BEHAVIOUR
  All storm state cleared: storm_active=False, queue cleared, phase=None, current_mine=None, elapsed=0, warning/border flash reset, all timers cancelled, bonus_foods cleared.

AC-10: PLATFORM COMPATIBILITY
  All 4 versions independent. Pygame: accumulator timing. Tkinter: root.after() scheduling. HTML/JS: setTimeout/setInterval. Console: tick-based (3 ticks Phase 1, 1 tick Phase 2).

AC-11: FOOD AND SNAKE COLOUR CONSTRAINTS
  Bonus food MUST be GREEN. Snake colour progression must not be affected.

TECHNICAL NOTES — STATE VARIABLES

Python: storm_active (bool), storm_queue (list), storm_phase (str|None: 'warning'|'explosion'), storm_current_mine (tuple|None), storm_phase_elapsed (float), storm_warning_flash_state (bool), storm_warning_flash_acc (float), border_flash_state (bool), border_flash_acc (float), bonus_foods (list).

JavaScript: stormActive, stormQueue, stormPhase, stormCurrentMine, stormPhaseTimer (setTimeout ID), stormWarningFlashState, stormWarningFlashTimer (setInterval ID), borderFlashState, borderFlashTimer (setInterval ID), bonusFoods.

NEW CONSTANTS (all versions):
  STORM_TRIGGER_COUNT=10, STORM_BORDER_COLOR_A=(255,0,0)/'#FF0000', STORM_BORDER_COLOR_B=(0,0,0)/'#000000', STORM_BORDER_FLASH_INTERVAL=0.2s/200ms, WARNING_DURATION=3.0s/3000ms, WARNING_FLASH_INTERVAL=0.2s/200ms, EXPLOSION_DURATION=1.0s/1000ms, EXPLOSION_COLORS=[(255,0,0),(255,136,0),(255,255,0),(255,255,255),(255,68,0)], CONSOLE_WARNING_CHAR='!', CONSOLE_EXPLOSION_CHAR='*', CONSOLE_STORM_LABEL='*** DETONATION STORM ***'.

RENDERING ORDER: 1.Background 2.Grid 3.Storm border (if active) 4.Explosion cells Phase2 5.Warning mine cell Phase1 6.Remaining mines (standard flash) 7.Bonus foods 8.Standard food 9.Snake 10.Score/UI 11.Game over overlay.

PHASE TRANSITION LOGIC:
  phase=='warning' and elapsed>=3.0s → transition to 'explosion', elapsed=0, spawn bonus food.
  phase=='explosion' and elapsed>=1.0s → pop next mine from queue as 'warning', or end storm if queue empty.

SUCCESS CRITERIA: SC-1 through SC-22 as defined in full user story. Key: storm triggers at 10, warning flash 3s, explosion 1s/3x3, snake kill Phase2 only, GREEN bonus food at Phase2 start, all timers cleared on restart, all 4 versions, all 7 docs updated.
