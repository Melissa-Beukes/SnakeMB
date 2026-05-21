# DataFlow Context Pack

Verified data flow, models, and persistence boundaries for the Snake Game codebase.

## 1. Data Models and Schemas

### Snake (in-memory)

A snake is a Python list of (x, y) integer tuples (head at index 0) plus three companion attributes:
- direction: one of UP=(0,-1), DOWN=(0,1), LEFT=(-1,0), RIGHT=(1,0).
- grow: bool. When True on a tick, the tail is not popped.
- color_index: integer index into SNAKE_COLORS (rotates on each food eaten).

The Pygame Snake adds animation_frames, current_frame, prev_head, next_head for sub-step interpolation.

### Food (in-memory)

- Pygame: Food instance with a position tuple.
- Tkinter / Console / HTML: a bare (x, y) tuple or [x, y] array stored at module scope.

### Mines (in-memory)

A list of (x, y) tuples. Mutated in place by spawn_mine. Cleared during a mine detonation explosion when the mine is consumed by its blast phase.

### Storm phase (in-memory state machine)

Set of variables (names vary slightly per implementation):
- storm_phase: one of "idle", "border_flash", "warning", "explosion".
- storm_phase_start: timestamp or tick counter that drove the phase entry.
- storm_mine_queue: ordered list of mine positions yet to detonate.
- bonus_food_positions: list of positions for the bonus food awarded per detonation (AC-7).

### Invincibility (in-memory)

- invincibility_active: bool.
- invincibility_time_remaining (Pygame) or invincibility_ticks_remaining (Console).
- invincibility_count: integer; persisted into high-score records when the game ends.

### High-score record (persisted, JSON)

Each entry is a dict with the keys:
- score (int)
- name (string, uppercased; 1 to 20 alphanumeric characters)
- date (string; UTC ISO-8601 with "Z" suffix)
- food_eaten (int, default 0)
- mine_shrinks (int, default 0)
- invincibility_count (int, default 0)

Persisted envelope:
```
{
  "schema_version": 2,
  "scores": [ <entry>, <entry>, ... ]   // at most 10, sorted descending by score
}
```

Legacy shape, auto-migrated on first read by leaderboard._unwrap_scores and leaderboard.load_scores:
```
[ <entry>, <entry>, ... ]
```

Verified by reading the live highscores.json at the root of the repository.

**Observed key-ordering variability (round-2 finding):** the live `highscores.json` contains two key orderings within the same `scores` array. Entries inserted natively by v2-aware code have `score`/`name`/`date` first; entries that flowed through `migrate_legacy_entries` have `food_eaten`/`mine_shrinks`/`invincibility_count` first because the migration helper merges the default-stats dict before the entry dict (defaults-first wins on key order in Python 3.7+ dict insertion-order semantics). This is a cosmetic artefact of the migration path described in section 2 "Migration pipeline"; it is not a schema violation and no code reads keys positionally. Verified by reading `highscores.json` lines 4-83.

## 2. Data Transformation Pipelines

### Mine spawn pipeline (per food eaten in Pygame; equivalent inline pipelines in other implementations)

1. score += 1.
2. spawn_mine(mines, snake_body, snake_direction, food_pos, score) is invoked.
3. Inside spawn_mine: target = 1 + score // 5; while len(mines) < target attempt up to 1000 random (cx, cy) candidates, each passed through is_valid_mine_position.
4. Validators in order: snake-body intersection, Manhattan distance <= 10 to any segment, projected-forward-path intersection, food coincidence, duplicate mine.
5. Valid candidates are appended.

### Storm pipeline (on STORM_TRIGGER_COUNT)

1. storm_phase transitions idle -> border_flash for the introductory beat.
2. border_flash -> warning, with the front of storm_mine_queue selected.
3. After WARNING_DURATION, phase moves to explosion; the 3x3 blast cells centred on the mine are recorded.
4. If snake head or any snake segment lies in a blast cell and invincibility_active is False, the game ends.
5. After EXPLOSION_DURATION, the consumed mine is removed and a bonus food is spawned for the player.
6. The next mine in the queue resumes the warning phase; when the queue empties, storm_phase returns to idle.

### Leaderboard insert pipeline

1. SnakeGame end-of-game collects food_eaten, mine_shrinks, invincibility_count.
2. HighScoreManager.is_high_score(score) checks qualification.
3. If qualified, the user is prompted for a name (Tkinter only, via simpledialog).
4. HighScoreManager.add_score validates the name (1-20 alphanumeric); raises ValueError on failure.
5. Loads current scores, appends new entry with UTC timestamp, sorts desc by score, truncates to top 10.
6. save_scores writes the v2 envelope to disk; on IOError the unsaved scores are silently discarded (best-effort durability).

### Migration pipeline (legacy -> v2)

1. load_scores reads JSON; if root is a list, calls migrate_legacy_entries.
2. Each entry is merged with default stats ({food_eaten:0, mine_shrinks:0, invincibility_count:0}); entry values win.
3. The migrated list is immediately persisted via save_scores, which writes the v2 envelope. Subsequent reads load the v2 form directly.

## 3. Input/Output Flows and APIs

There are no remote APIs. All I/O is local.

### Inputs
- Keyboard: pygame.event.poll (Pygame), root.bind on KeyPress (Tkinter), stdin via input() (Console), addEventListener("keydown") on document (HTML).
- File: highscores.json read on game-over qualification check; music\chiptune_triumphant.wav read on invincibility start (Pygame and HTML); the Tkinter implementation uses winsound.PlaySound with a hard-coded absolute path to the same WAV file.

### Outputs
- Screen: pygame.display.flip (Pygame), Canvas item creation/recolouring (Tkinter), sys.stdout writes (Console), Canvas2D fillRect (HTML).
- File: highscores.json written via json.dump (indent=2) on every add_score that progresses past the duplicate check.
- Audio: winsound.PlaySound on Tkinter; pygame.mixer.music on Pygame; HTMLAudioElement.play on HTML; none on Console.

### Public function surface
- game_logic.py exposes seven pure helpers (see code.md).
- leaderboard.py exposes the HighScoreManager class (see code.md).
- snake_game_tkinter.py exposes format_leaderboard_message as a module-level pure function so it can be unit-tested independently of Tkinter.

## 4. Database Interactions and Queries

There is no database. The single persistence target is the JSON file highscores.json.

- Storage shape: a single JSON object (v2 envelope) or, for legacy files, a bare JSON array.
- Access pattern: read-modify-write. Every add_score reads the whole file, mutates the in-memory list, sorts, truncates, then writes the whole file.
- Concurrency: not safe across processes. No locking. Only one game instance is expected to write at a time.
- Backup: none. There is no .bak rotation, no atomic write (no tmp + rename), no checksum.

## 5. State Management and Data Persistence

In-memory state is owned per implementation:
- Pygame: module-level state plus the Snake and Food instances.
- Tkinter: all state held on the SnakeGame instance.
- Console: module-level state mutated by the main loop.
- HTML: top-level let bindings in the inline script.

State transfer between implementations is impossible directly - only via the shared highscores.json file. A score earned in any implementation that integrates the leaderboard (currently only Tkinter; the others do not call HighScoreManager) is written to the same file. Scores earned in Pygame, Console, or HTML are not persisted because those implementations do not currently invoke HighScoreManager.add_score.

Lifecycle:
- Cold start: highscores.json may not exist; load_scores returns [] without error.
- Normal game: in-memory state evolves per tick; no intermediate persistence.
- Game over: persistence happens once via add_score (Tkinter only).
- Process exit: no flush required; nothing additional is written.

### Invincibility availability constraint (Pygame, round-2 finding)

In `snake_game.py` the only branch that sets `super_food_position` to a non-`None` value is at lines 367-376, inside the warning-to-explosion transition of the Mine Detonation Storm. There is no normal-play spawn path. As a result, the data-flow path "score >= super-food threshold → spawn super-food → eat super-food → enter invincibility" cannot fire on the Pygame runtime outside an active MDS event. The Invincibility Power-Up is therefore reachable on Pygame **only** during a storm (and only when `super_food_mine_counter == super_food_mine_index`). This is a behavioural divergence from the Tkinter and HTML runtimes which spawn super-food independently of the storm machine. See `code.md` section 2 for the function-level cross-reference.

## 6. Data Validation and Sanitisation

- Name validation in HighScoreManager.validate_name: rejects empty strings, strings longer than 20 characters, and strings containing non-alphanumeric characters (str.isalnum is False on punctuation, whitespace, and unicode symbols outside the alphanumeric category).
- name.upper() is applied on insert so leaderboard names are case-normalised.
- Schema migration is defensive: missing stats fields are filled with zeros, but values that already exist are preserved (dict merge with defaults first, entry second).
- JSON parsing errors are swallowed and treated as empty leaderboard (load_scores returns []).
- IOError on save is swallowed; the function returns False so the caller can detect partial-failure (add_score uses this to re-read the prior leaderboard and discard the unsaved entry, keeping in-memory and on-disk state consistent).
- spawn_mine candidate validation: five-stage rejection in is_valid_mine_position (see code.md). No exceptions raised; invalid candidates are simply retried.
- Direction inputs are filtered at the source: only the arrow keys (or WASD on Console) produce direction changes; reversal is rejected by tuple negation comparison in change_direction.
- There is no validation of the music file path or contents; if missing, the audio call raises but is not caught - in practice the file exists at music/chiptune_triumphant.wav, but the hard-coded Pygame path C:\Users\GrahamSaunders\Downloads\snake_game_v1.1.0\music\chiptune_triumphant.wav will not resolve outside the original developer machine. (The Pygame implementation does wrap the load in `try/except Exception as e` at `_start_invincibility_music` and prints a warning to `sys.stderr`, so the audio failure is non-fatal in that runtime.)

## 7. Data-flow defects discovered in round-2 enrichment

- **Snake never moves on non-super-food ticks (Console)**: `snake_game_console.py` line 287 has `snake.move()` indented inside the super-food collision branch. The per-tick data flow described in section 1 is broken: the snake only advances on the rare tick in which the player ate a super-food. The file additionally fails to parse (see `risk.md` section 2) so this defect is currently latent behind a syntax error.
- **Storm phase countdown unbounded by `if`-guard (Console)**: lines 290-291 — `storm_phase_ticks -= 1` is at the same indent level as the `if not paused and storm_active:` header, so it would (if it parsed) decrement every tick regardless of pause state or storm activation. This violates the data-flow contract in section 2 ("storm pipeline").
- **Super-food draw path crashes on first flash (Pygame)**: `snake_game.py` line 551 uses `SUPER_FOOD_COLOR_A` which is not defined, raising `NameError`. The data-flow path "score >= super-food threshold -> spawn super-food -> render flashing super-food" is therefore broken at the render step.
- **Pause-overlay draw path crashes (Pygame)**: `snake_game.py` line 477 calls a function that does not exist. Latent until `paused` is ever set to True.
- **HTML globals `paused`, `showRules` undeclared**: section 5 above documents this as a code-quality issue; in non-strict mode the data flow continues because the browser creates the globals; in strict mode the read at line 443 (`if (paused) return;`) raises `ReferenceError` and the per-tick data flow is broken.
- **Pygame rules splash never drawn**: `snake_game.py` line 208 defines `draw_rules_screen(screen)` but the draw block at lines 456-479 never calls it. The `show_rules = True` flag at line 268 silently consumes the first key press. The "rules splash → game start" leg of the start-up data flow is dead on the Pygame runtime — the player goes straight from the cold-start render to gameplay with one key press swallowed in between. See `risk.md` section 1.3.
- **Pygame Mine Detonation Storm phase transition mis-nested**: `snake_game.py` lines 388-399. The block that pops `storm_queue` and transitions back to the `'warning'` phase sits inside the `for dy in range(-1, 2):` inner blast-cell loop, so the storm-pipeline transition described in section 2 step 6 fires on every iteration of the inner loop rather than once per explosion frame. The storm phase machine on the Pygame runtime therefore deviates from the contract described in section 2 the moment it reaches its first `explosion` phase. See `risk.md` section 1.4.

All seven issues are catalogued with file:line citations in `risk.md`.

## 8. Cross-references

- `risk.md` — every defect named in section 7 is enumerated there with the verification method used to confirm it.
- `code.md` section 7 — broader hazard register (hard-coded paths, fragile tests, stale standalone scripts).
- `risk.md` section 5b — prioritised mitigation order for the same defects.
- `decisions.md` — historical record of the user-story acceptance criteria that the data-flow pipelines in section 2 implement.

## 9. Mine Detonation Storm Phase Transition Logic (canonical)

Phase transitions apply identically across all four runtimes (timing units differ
per ADR-007 in `decisions.md`).

- **storm start**: on a food-eat event, if total mine count reaches
  `STORM_TRIGGER_COUNT` (10) and no storm is active, shuffle the full mine list
  into `storm_queue` and enter `'warning'` for the first mine.
- **warning -> explosion**: when `storm_phase == 'warning'` and
  `elapsed >= WARNING_DURATION` (3.0 s / 3 ticks), transition to `'explosion'`,
  reset elapsed to 0, and spawn one bonus food at the mine centre cell.
- **explosion -> next warning or storm end**: when `storm_phase == 'explosion'`
  and `elapsed >= EXPLOSION_DURATION` (1.0 s / 1 tick), pop the next mine from
  `storm_queue` into `'warning'`; if the queue is empty set `storm_phase = None`
  and `storm_active = False`.
- **storm abort**: on snake death during any phase, immediately clear
  `storm_active`, `storm_queue`, and all phase state.
- **restart**: `reset_game()` clears `storm_active`, `storm_queue`,
  `storm_phase`, `storm_current_mine`, `storm_phase_elapsed`, flash accumulators,
  and `bonus_foods`.

Note: the Pygame implementation has a confirmed mis-nesting at lines 388-399
where the explosion->next phase transition fires inside the `for dy` blast-cell
loop rather than after it. See `risk.md` section 5b for the full defect record.

Source: `mine-detonation-storm/user-story.md` AC-1, AC-3, AC-7, AC-9;
`decisions.md` ADR-024.
