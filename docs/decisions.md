# Decisions Context Pack

Architectural decision records and rationale derived from in-repo documentation (flashing-mines/, mine-detonation-storm/, Auto-PR-Solution.md, STRUCTURE.md) and observed source code patterns. Every entry references its evidence.

## ADR-001: Three runtimes plus a browser implementation (no shared core beyond game_logic.py)

- Decision: Maintain four independent implementations - Pygame, Tkinter, Console, HTML - rather than one cross-runtime engine with a thin presentation layer.
- Evidence: snake_game.py is the only file that imports game_logic.py; snake_game_tkinter.py, snake_game_console.py, and snake_game.html each re-implement equivalent logic.
- Rationale: Each runtime has distinct timing (frame-loop vs after-callback vs blocking-input vs setInterval) and audio APIs (pygame.mixer vs winsound vs none vs HTMLAudioElement). README.md presents them as three positioned-product variants ("Easiest", "No Dependencies", "Enhanced Graphics").
- Trade-off: Feature parity must be maintained by hand. The Mine Detonation Storm and Invincibility features therefore appear in all four implementations (verified) - any future change must touch four files.
- Alternatives considered: Extracting a runtime-agnostic core (would have required a renderer abstraction). Not pursued; not justified at current scope.

## ADR-002: Pure-function game_logic.py for testability

- Decision: Concentrate all deterministic, side-effect-free rules in game_logic.py with explicit parameter passing.
- Evidence: tests/test_game_logic.py exercises seven helpers; pytest.ini scopes test collection to tests/ exactly because that is where the unit-testable surface lives.
- Rationale: Pure functions are trivially testable without GUI or random-seed mocking.
- Trade-off: spawn_mine still depends on random; tests cope by seeding random or by asserting properties rather than exact positions.
- Alternative considered: a single GameState dataclass. Rejected because the four runtimes do not share state shapes (e.g. animation_frames is Pygame-only).

## ADR-003: Top-10 leaderboard, JSON envelope, single-file persistence

- Decision: Persist the leaderboard to highscores.json with schema_version 2 envelope.
- Evidence: leaderboard.py SCHEMA_VERSION constant; live highscores.json file with the v2 envelope.
- Rationale: Smallest possible persistence layer; human-readable; no external runtime dependency; trivially diffable.
- Trade-off: Read-modify-write on every insert (no append log); no atomic-write (no tmp+rename). Acceptable for a single-process game; documented as a known limitation in risk.md.

## ADR-004: Auto-migrate legacy bare-list highscores to v2 envelope on first read

- Decision: When load_scores encounters a JSON list at the root, convert it to v2 form and persist immediately.
- Evidence: leaderboard.load_scores logic; HighScoreManager._unwrap_scores delegates to migrate_legacy_entries.
- Rationale: Forward compatibility for users with pre-stats highscores. Migration is partial-safe (entry values override defaults), so re-running the migration is idempotent.
- Trade-off: An older snapshot of the file restored after migration would be silently upgraded again on read - acceptable because the upgrade only adds fields.

## ADR-005: Name validation is strictly 1 to 20 alphanumeric characters

- Decision: HighScoreManager.validate_name enforces 1 <= len(name) <= 20 AND name.isalnum().
- Evidence: leaderboard.py validate_name; test_leaderboard.py TestNameLengthBoundary class.
- Rationale: Eliminates injection of newlines, control characters, or unbounded-length strings into a persisted text file; isalnum is unicode-aware, allowing internationally-named players.
- Trade-off: Punctuation and spaces are rejected even where culturally common (e.g. "O'Brien", "Mary-Jane"). Documented intentionally; consistent across all tests.

## ADR-006: Storm trigger by absolute mine count, not score

- Decision: STORM_TRIGGER_COUNT = 10 is checked against the live mines list length.
- Evidence: snake_game.py, snake_game_tkinter.py, snake_game_console.py, snake_game.html - all share the same trigger constant and check.
- Rationale (per mine-detonation-storm/Plan.md): tying the storm to mine density rather than score makes the feature self-balancing across implementations whose grid sizes differ (30x30 vs 20x20 in console). Same player skill yields the same storm cadence in absolute terms.
- Trade-off: Console implementation's 20x20 grid reaches density faster than the 30x30 grid in others - this is acceptable per the lessons-learned notes.

## ADR-007: Storm uses platform-native timing primitives

- Decision: Do not unify timing across implementations.
- Evidence:
  - Pygame: real-time accumulator with dt = clock.tick(60)/1000.
  - Tkinter: root.after(ms, callback) cascade.
  - Console: integer tick counters (WARNING_TICKS=3, EXPLOSION_TICKS=1).
  - HTML: setInterval(tick, gameSpeed) plus setTimeout for phase transitions.
- Rationale (per mine-detonation-storm/Plan.md and post-implementation-lessons-learned.md): Each platform has an idiomatic, lowest-friction timing mechanism. Forcing one mechanism would bloat each implementation.
- Trade-off: Three sets of constants (seconds, ticks, milliseconds) must remain in sync conceptually. Verified by reading each file.

## ADR-008: Console implementation wraps; others wall-collide

- Decision: Console wraps the snake at the grid edges via modulo arithmetic; Pygame, Tkinter, and HTML treat off-grid as game over.
- Evidence: snake_game_console.py Snake.move uses % GRID_WIDTH and % GRID_HEIGHT; the others call check_wall_collision or its inline equivalent.
- Rationale: Console redraw is heavy; wall collisions plus rapid restart would feel unresponsive given the blocking input model.
- Trade-off: Behaviour is non-uniform across runtimes; documented in README.md and STRUCTURE.md only implicitly.

## ADR-009: No external dependencies beyond pygame, pytest, stdlib

- Decision: Refuse third-party packages except pygame (and pytest for tests).
- Evidence: requirements.txt contains exactly pygame==2.5.2 and pytest.
- Rationale: Tkinter version aims at zero-install; console version is stdlib-only; HTML version is browser-native. Pygame is justified by "Enhanced Graphics" (README.md).
- Trade-off: Hand-rolled JSON, datetime, and audio glue. The team accepts this in exchange for trivial cross-platform install.

## ADR-010: Manual backup files instead of branches

- Decision: Use .bak, .bak-mds, .bak-pre-white-food sibling files for rollback safety.
- Evidence: Eight backup files exist at the repo root next to their live counterparts.
- Rationale: Tangible "last good" snapshot inside the working tree, instantly diffable even without git tooling. Captured by mine-detonation-storm/ and flashing-mines/ ToDo.md entries that mark snapshots at phase boundaries.
- Trade-off: Pollutes the file tree; duplicates content already in git history. Tolerated for feature-branch ergonomics.

## ADR-011: Test layout split into pytest tests/ and root-level unittest scripts

- Decision: tests/ (pytest, scoped by pytest.ini testpaths=tests) hosts the game-logic suite; root-level files test_leaderboard.py, test_snake_game_tkinter_display.py, test_food_color.py use unittest and require explicit invocation.
- Evidence: pytest.ini contents; the unittest.main() guard at the bottom of each root-level test file.
- Rationale: Faster default suite (only pure logic) for tight inner loop. Heavier suites (leaderboard I/O, Tkinter display, regex-source-parse) are opt-in.
- Trade-off: Easy to forget the root tests during a regression sweep; lessons-learned in mine-detonation-storm/post-implementation work flag this as a future improvement.

## ADR-012: Documentation lives next to the feature it documents

- Decision: Each major feature has a self-contained folder with Plan.md, Build.md, ToDo.md, user-story.md, and post-implementation-lessons-learned.md.
- Evidence: flashing-mines/ and mine-detonation-storm/ folders.
- Rationale: Documentation that the team actively maintained during implementation is therefore high-fidelity; the user story + acceptance criteria sit next to the build guide that ships the acceptance.
- Trade-off: Discovery requires opening the folder; addressed by the top-level docs/ Context Pack set (this file is the top-level index of decisions).

## ADR-013: AAFM PR-creation regex bug fix (operational tooling, not gameplay)

- Decision: Auto-PR-Solution.md documents the fix to a regex in aafm-server.js that previously rejected repository names containing dots (e.g. snake_game_v1.1.0).
- Evidence: Auto-PR-Solution.md sections 1-3 explain three errors (401 Bad credentials, 422 head field validation, 404 Not Found) and pin the root cause to the regex pattern github.com[/:]([^/]+)/([^/.]+); the fix is to drop the dot exclusion in the second capture group.
- Rationale: Preserves dot-containing names in upstream tooling; surfaced after the original repository was tagged with semver-style identifiers.
- Trade-off: Tool-side change; nothing in the game code changed.

## ADR-014 (FM-D1): Pygame mine collision wins over food on same cell

- Decision: In `snake_game.py`, the mine collision check runs **before** `snake.eat_food()` so that if the snake somehow lands on a cell containing both, the mine damage is processed.
- Evidence: `flashing-mines/post-implementation-lessons-learned.md` decision D1; verified in source.
- Rationale: Treats mine hits as a damage event independent of food consumption.

## ADR-015 (FM-D2): Console mine path projection wraps via modulo with a visited-set guard

- Decision: `snake_game_console.py` `spawn_mine()` projects the snake's forward path through the grid using modulo wrapping (matching the console runtime's wrapping movement) and uses a `visited` set to detect cycles.
- Evidence: `flashing-mines/post-implementation-lessons-learned.md` decision D2 and deviation C1; verified by reading the spawn helper.
- Rationale: The console grid wraps, so a naive while-loop projection would loop forever once the path returns to its origin.

## ADR-016 (FM-D3): Tkinter reset_game uses hasattr guard for flash timer cancellation

- Decision: `_flash_after_id` is accessed via `hasattr(self, '_flash_after_id')` inside `reset_game()`.
- Evidence: lessons-learned D3.
- Rationale: `reset_game()` is invoked once during `__init__` before any timer has been scheduled; without the guard, the first invocation raises `AttributeError`.

## ADR-017 (FM-D4): HTML mine collision is checked before unshift

- Decision: In `snake_game.html`, the mine collision check operates on the new `head` value before `snake.unshift(head)` is called.
- Evidence: lessons-learned D4 and deviation C2.
- Rationale: Same convention as the existing wall and self-collision checks; `snake.length === 0` post-shrink correctly handles the edge case where the body (excluding the new head) is empty.

## ADR-018 (MDS): Bonus food is GREEN and only spawned at Phase 2 start

- Decision: Per `mine-detonation-storm/user-story.md` AC-6 and AC-11, the bonus food awarded by a detonation must be RGB (0, 255, 0) / `#00FF00` and must spawn exactly at the start of explosion Phase 2 at the mine centre cell.
- Evidence: `user-story.md` AC-6, AC-11; `feature.json` `feature_input.constraints` item 3.
- Rationale: Visual consistency across implementations; uses a colour distinct from both standard food (today: white / hot pink depending on runtime) and the snake palette.
- Trade-off / drift: The standard (non-bonus) food has since drifted from green to white (Pygame, HTML, Console) and hot pink (Tkinter). The original AC-11 constraint covered bonus food, not standard food; the drift is documented in `risk.md` section 5b and ADR-021 below.

## ADR-019 (MDS): Storm trigger is evaluated only on food-eat events, not on every tick

- Decision: AC-1.b — the trigger check runs only inside the food-eat code path that pushes mine count up.
- Evidence: `user-story.md` AC-1.b; verified by inspecting each implementation.
- Rationale: Mine count can only grow on food eaten (`spawn_mine` is called there); evaluating on every tick would be wasted work.

## ADR-020 (MDS): No nested storms — trigger is suppressed while a storm is active

- Decision: AC-8.c.
- Evidence: `user-story.md` AC-8.
- Rationale: Mine count is allowed to grow during a storm (normal spawning continues), but the new mines do not enter the current detonation queue and a fresh trigger is not raised. This prevents an unbounded chain of overlapping storms.

## ADR-021: Documentation drift acknowledged, white-food era is a partial rollout

- Decision: The "white food" feature was implemented in a separate, follow-on edit cycle whose backup snapshots are present as `*.bak-pre-white-food`. The rollout was applied to Pygame and HTML, partially to Console (still emits via bright-white ANSI), and was missed entirely in Tkinter (still hot pink) and in the README and glossary.
- Evidence: Three `.bak-pre-white-food` files exist; `snake_game.py` line 21 and `snake_game.html` line 119 show the white value; `snake_game_tkinter.py` line 15 still shows hot pink with a stale "ALWAYS YELLOW" comment.
- Rationale: Captured here so subsequent work knows the partial state. The decision to keep or revert the white-food change has not been recorded in any ADR before this.
- Trade-off: until completed or reverted, the four implementations disagree visually.

## ADR-022: Retain root `STRUCTURE.md` as a flagged stale relic; do not delete it in the documentation pass

- Decision: The root-level `STRUCTURE.md` is preserved on disk but is explicitly marked stale by `docs/structure.md` section 1.2 and `docs/risk.md` section 3. It will NOT be deleted as part of any documentation audit (round-2 or round-3) because deletion is a destructive repo-shape change and falls outside Objective 6 of `docs/decisions.md` ("Update the existing /docs Context Packs in place; do NOT create new context files").
- Evidence: `docs/structure.md` section 1.2 documents the staleness (lists non-existent `.cursor/commands/`, `.vscode/`, `.cursor/README.md`; says three runtimes; omits `game_logic.py`, `leaderboard.py`, `snake_game_console.py`, `tests/`, `highscores.json`, `music/`, feature folders, backups). `docs/structure.md` is now the canonical structure reference.
- Rationale: Removing `STRUCTURE.md` would surprise external tooling or onboarding scripts that may grep for it; the file's staleness is sign-posted in three Context Packs and the audit log, so the risk of it misleading a reader has been documented away rather than fixed by deletion. Deletion remains available as a future enhancement (Suggested Future Enhancements item 1 below).
- Trade-off: A stale top-level file continues to exist in the working tree and can drift further. Mitigated by the explicit stale-marker references in `docs/structure.md`, `docs/risk.md`, and `docs/structure.md`.
- Cross-ref: `docs/decisions.md` finding C.6 and the previously-skipped C.6.c remediation item.

## Future considerations and known technical debt (captured, not yet acted on)

- Cross-runtime asset paths: the absolute Windows path embedded in snake_game.py and snake_game_tkinter.py for the invincibility music should be replaced with a path relative to __file__. Already a known issue (flashing-mines/post-implementation-lessons-learned.md L2).
- README.md still instructs cd C:\cursor\snake_game - stale.
- verify_color.py asserts the historical light-blue colour (100, 200, 255) while source now sets (255, 255, 255). Script must be updated or removed.
- No automated invocation of the root-level unittest scripts; ideally pytest discovery is widened or a make/run target is added.
- highscores.json write is not atomic; a power loss mid-write could corrupt the file. The graceful corruption handling in load_scores would simply return [] - acceptable today; an atomic tmp+rename is a candidate improvement.
- Pygame and HTML implementations do not call HighScoreManager.add_score; only the Tkinter version writes to the leaderboard. Either extend persistence to the others or document the constraint in README.md.

## ADR-023: Flashing Mines feature delivery (completed 2026-03-05)

- Decision: Implement the Flashing Mines feature across all four runtimes as the
  prerequisite for Mine Detonation Storm.
- Delivery: 62-task checklist (flashing-mines/ToDo.md) all closed. Syntax
  validation used `py -c "import ast; ast.parse(open(..., encoding='utf-8').read())"`.
  Manual gameplay testing confirmed by the user on 2026-03-05.
- Key implementation decisions (from flashing-mines/post-implementation-lessons-learned.md):
  D1: Pygame mine collision processed before `snake.eat_food()` so a same-cell mine wins.
  D2: Console `spawn_mine()` uses modulo wrapping for path projection and a `visited` set to break cycles.
  D3: Tkinter `reset_game()` uses `hasattr(self, '_flash_after_id')` because the attribute does not exist on the first call.
  D4: HTML mine collision check happens before `snake.unshift(head)`.
- Deviations from plan: C1 (Console visited-set not in Build.md). C2 (HTML shrink-before-head-prepend order kept as Build.md specified).
- Lessons: L1 PowerShell uses `;` not `&&`. L2 `snake_game_console.py` requires `encoding='utf-8'`. L3 Use `py` launcher. L4 All verification is manual per .cursorrules Rule 10.
- Artefacts: flashing-mines/flashing-mines-plan.md, flashing-mines/Build.md, flashing-mines/ToDo.md, flashing-mines/post-implementation-lessons-learned.md.

## ADR-024: Mine Detonation Storm feature delivery (started 2026-03-06)

- Decision: Implement Mine Detonation Storm (MDS-001) across all four runtimes on
  top of the Flashing Mines baseline.
- User story: MDS-001 with AC-1 through AC-11 (mine-detonation-storm/user-story.md).
  All phases 1-6 marked complete in mine-detonation-storm/ToDo.md.
- Build constraints (from mine-detonation-storm/feature.json): all four game files
  standalone; no new external deps; bonus food must be green (AC-11); snake colour
  progression must not be broken; compatible with Flashing Mines state variables;
  use `py`; use `;` in PowerShell; open console file with encoding='utf-8'; no
  automated tests; all seven /docs files updated on completion.
- Artefacts: mine-detonation-storm/Plan.md (~380 LOC), mine-detonation-storm/Build.md
  (~1700 LOC), mine-detonation-storm/ToDo.md, mine-detonation-storm/user-story.md,
  mine-detonation-storm/feature.json (status: in-progress at last edit; PR URL not
  populated), mine-detonation-storm/run-log.md.
- Post-delivery errata: bonus food on Pygame and HTML remains green (AC-11 compliant).
  Standard food drifted to white/hot-pink in a subsequent edit cycle (see ADR-021).
  Pygame super-food spawn is MDS-only (see `code.md` section 2 Invincibility
  availability constraint).
- AC summary: AC-1 trigger=10 mines, no nesting; AC-2 border flash red/black 0.2 s;
  AC-3 random order, 3 s warning + 1 s explosion each; AC-4 EXPLOSION_COLORS palette;
  AC-5 head in Phase 2 = death unless invincible; AC-6 green bonus food at mine centre
  at Phase 2 start; AC-7 storm ends when queue empty or snake dies; AC-8 new mines not
  appended to active queue; AC-9 restart clears all storm state; AC-10 platform-native
  timing; AC-11 bonus food green, snake palette unaffected.

## Suggested Future Enhancements (repo audit findings, not yet actioned)

1. Delete `STRUCTURE.md` from the repo root -- superseded by `docs/structure.md` and heavily out of date.
2. Consolidate the three cursor/roo rule copies (`docs/.cursorrules`, `.cursor/rules/rules.mdc`, `.roo/rules/rules.md`) into one canonical file.
3. Add a `.gitignore` covering `__pycache__/`, `.pytest_cache/`, `highscores.json`, `*.bak*`.
4. Add a CI workflow file that runs `pytest` plus the three root-level unittest suites automatically.
5. Add an `import snake_game_console` smoke test and a Pygame headless draw-path smoke test (`SDL_VIDEODRIVER=dummy`).
6. Extract a runtime-agnostic core to eliminate four-way hand-synchronisation (see ADR-001).
7. Replace `os.system("cls")` in `snake_game_console.py` with an ANSI cursor-home sequence.
8. Make `leaderboard.save_scores` atomic via tmp+rename.
9. Update `README.md`: four-runtime topology, correct colour claims, remove stale `cd C:\cursor\snake_game`.
10. Update `run_pygame_version.bat` to drop the stale "light blue food" banner.
11. Replace `test_food_color.py` regex parsing with a direct attribute import.
12. Verify `Auto-PR-Solution.md` claims line by line (treated as historical context only so far).
13. Decide whether to retain or remove the `.bak*` snapshots (ADR-010 tolerates them).
