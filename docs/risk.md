# Risk Context Pack

Verified risks, technical debt, and mitigation recommendations sourced from observed code and in-repo documentation. Speculative risks are not included; every entry cites its evidence.

## 1. Security Concerns

### Hard-coded absolute paths to a specific user account

- Evidence: snake_game.py line 53 sets INVINCIBILITY_MUSIC_PATH to r"C:\Users\GrahamSaunders\Downloads\snake_game_v1.1.0\music\chiptune_triumphant.wav". snake_game_tkinter.py uses an equivalent hard-coded path with winsound.PlaySound. pytest.bat invokes a pytest.exe under the same user profile.
- Impact: Reveals a developer username in committed source. Not a credential exposure, but it is information disclosure and an immediate portability defect.
- Mitigation: Replace with os.path.join(os.path.dirname(__file__), "music", "chiptune_triumphant.wav") in both Python files; use plain "pytest" on PATH in pytest.bat.

### No authentication / authorisation surface

- Evidence: Codebase has no network calls or user accounts.
- Impact: None for the gameplay layer. The Auto-PR-Solution.md notes from the operational toolchain are unrelated to runtime security of the game.

### File I/O on highscores.json without atomic write

- Evidence: leaderboard.save_scores opens the file in "w" mode and json.dumps in place.
- Impact: A crash, power loss, or kill during the write window leaves a truncated or partial file. load_scores will catch json.JSONDecodeError and return [], so the user loses their entire leaderboard rather than just the last entry.
- Mitigation: Write to highscores.json.tmp then os.replace to highscores.json (atomic on POSIX and on Windows where the source and destination are on the same volume).

### No input sanitisation beyond name validation

- Evidence: validate_name allows only 1-20 alphanumeric characters; this is sufficient for a local file. No other user-supplied data exists in the gameplay loop.
- Impact: None observed. Documented for completeness.

## 2. Performance Bottlenecks

### Console implementation full-screen redraw

- Evidence: snake_game_console.py calls os.system("cls" if os.name == "nt" else "clear") each tick before printing the grid.
- Impact: Spawns a subprocess on every redraw. On Windows this is markedly more expensive than ANSI cursor-home; it bounds achievable tick rate.
- Mitigation: Emit "\033[H" or "\033[2J\033[H" instead of forking cls. Listed in flashing-mines/post-implementation-lessons-learned.md as future work.

### Mine spawn search is up to 1000 attempts per mine, O(n) per attempt

- Evidence: game_logic.spawn_mine; the Manhattan-distance check loops over the entire snake body.
- Impact: Worst-case CPU spike when the grid is saturated; can stall the food-eaten event by several milliseconds on long snakes. The cap of 1000 prevents an infinite loop but silently under-spawns when no valid slot exists.
- Mitigation: Switch to candidate-set construction (precompute the set of valid cells once per spawn batch) and sample from it. Already discussed in flashing-mines/post-implementation-lessons-learned.md.

### Tkinter Canvas redraws every item per tick

- Evidence: snake_game_tkinter.py draw method recreates or recolours canvas items on every move_snake invocation.
- Impact: Tkinter Canvas is single-threaded and not GPU-accelerated; redraw cost grows linearly with the cell count.
- Mitigation: Track canvas item IDs and only update those that change.

### Pygame frame loop runs at clock.tick(60) regardless of player skill

- Evidence: pygame.time.Clock(60) is invoked unconditionally; sub-step animation_frames=5 yields ~12 logical moves per second.
- Impact: Acceptable for gameplay. Documented for completeness.

## 3. Technical Debt and Maintenance Issues

### Four parallel implementations must be hand-synchronised

- Evidence: Feature parity across snake_game.py, snake_game_tkinter.py, snake_game_console.py, snake_game.html for both Flashing Mines and MDS-001.
- Impact: Any new feature requires four edits. Tests verify Pygame logic only via game_logic.py; the other three runtimes have no behavioural test coverage.
- Mitigation: Extract a render-agnostic state module that the four runtimes drive. Documented as a future consideration in decisions.md ADR-001.

### Stale or contradictory documentation

- Evidence: README.md instructs cd C:\cursor\snake_game which does not match this repository path. verify_color.py expects FOOD_COLOR (100, 200, 255) but the live value is (255, 255, 255). `run_pygame_version.bat` line 2 still echoes "Running Pygame version (snake_game.py) with light blue food..." while the live value is white (see `risk.md` section 5b). `STRUCTURE.md` at the repository root is heavily out of date — it claims `.cursor/commands/`, `.vscode/`, a `.cursor/README.md`, and only three runtimes; none of those directories exist and there are in fact four runtimes (verified by directory enumeration; see `docs/structure.md` for the accurate map).
- Impact: Confuses new contributors; verify_color.py prints a misleading negative; the batch-file banner mis-describes the build; `STRUCTURE.md` actively mis-describes the repo topology and the available developer affordances.
- Mitigation: Delete verify_color.py (replaced by tests), update README.md with relative paths, rewrite the `run_pygame_version.bat` banner, and treat `docs/structure.md` as the canonical structure (consider deleting `STRUCTURE.md` per Suggested Future Enhancements in `decisions.md`).

### Cursor / Roo rule files duplicated in three locations

- Evidence: `docs/.cursorrules` (107 lines), `.cursor/rules/rules.mdc` (109 lines, with an `alwaysApply: true` MDC header), and `.roo/rules/rules.md` (109 lines) all encode the same mandatory-reference-doc rules. Verified by re-reading the three files; the body content matches from line 3 onwards.
- Impact: drift risk — updating any one of the three without the others creates contradictions that the AI assistant will surface inconsistently depending on which tool is loaded.
- Mitigation: pick one canonical source (the `docs/.cursorrules` file already exists) and replace the other two with references or a build step that regenerates them. Logged for follow-up in Suggested Future Enhancements in `decisions.md`.

### Backup files committed alongside source

- Evidence: Eight .bak / .bak-mds / .bak-pre-white-food files exist next to their live counterparts.
- Impact: Duplicates content already in git; pollutes diff and search; risks editing the wrong file.
- Mitigation: Remove the .bak files; rely on git tags or branches for rollback safety.

### Root-level unittest scripts not collected by default pytest run

- Evidence: pytest.ini sets testpaths = tests. test_leaderboard.py, test_snake_game_tkinter_display.py, and test_food_color.py live at the repo root and must be invoked manually.
- Impact: Easy to ship a regression in leaderboard, tkinter display, or food colour without noticing locally.
- Mitigation: Either move the suites into tests/, or widen testpaths in pytest.ini.

### test_food_color.py reads source as text

- Evidence: test_food_color.py opens snake_game.py and runs a regex against the FOOD_COLOR assignment.
- Impact: Reformatting the assignment line, adding a comment, or splitting onto multiple lines breaks the test even when behaviour is correct.
- Mitigation: Import snake_game and assert against the module attribute (the regex was historically used to avoid importing pygame in CI; with pygame in requirements.txt this is no longer needed).

### highscores.json is in the working tree

- Evidence: highscores.json is present at the repository root with real score entries.
- Impact: Personal leaderboards committed; merge conflicts on contention; risks losing scores on git reset.
- Mitigation: Add highscores.json to .gitignore (no .gitignore is verified in the file inventory, so a new one is needed) and ship an empty seed only.

### tests/__init__.py is empty

- Evidence: tests/__init__.py is empty.
- Impact: None functionally; included only because some pytest configurations expect a package marker.
- Mitigation: Acceptable; documented for context.

## 4. Scalability Limitations

### Fixed grid sizes

- Evidence: Grid is 30x30 for three of four implementations and 20x20 for the console; values are compile-time constants.
- Impact: No runtime tuning, no responsive resize on window-size changes.
- Mitigation: Read grid dimensions from a JSON config file at startup, or compute from the actual canvas size in HTML and Tkinter.

### Single-file persistence not safe for concurrency

- Evidence: leaderboard.save_scores uses a plain open(filepath, "w") without file locking.
- Impact: Two simultaneously-running instances of the game would race; last-write-wins corruption is possible.
- Mitigation: Use fcntl / msvcrt locks; or move to SQLite if multi-process play is ever supported.

### Top-10 cap is hard-coded

- Evidence: leaderboard.add_score does scores = scores[:10] and is_high_score compares against scores[-1] only when len == 10.
- Impact: No leaderboard expansion without code change.
- Mitigation: Promote the 10 to a module constant alongside SCHEMA_VERSION; passable risk at current scope.

## 5. Dependencies and External Risks

### pygame is a single point of failure for the Enhanced version

- Evidence: requirements.txt pins pygame==2.5.2.
- Impact: pygame 2.5.2 requires Python 3.7-3.13 per README.md. Python 3.14 already breaks Pygame today (README.md says: "Works on Python 3.7-3.13"). The pytest.bat hard-codes Python314 path - so the Pygame implementation cannot be exercised using the same Python install that runs the test suite on the original developer machine.
- Mitigation: Either upgrade pygame when it gains 3.14 support, or document the dual-environment requirement explicitly.

### winsound is Windows-only

- Evidence: snake_game_tkinter.py imports winsound at module top.
- Impact: import error on Linux / macOS prevents the Tkinter version from running at all (the import is unguarded).
- Mitigation: Guard the import inside try/except ImportError and skip audio if unavailable.

### HTML implementation depends on browser audio autoplay policy

- Evidence: snake_game.html plays new Audio('music/chiptune_triumphant.wav') on invincibility start.
- Impact: Modern browsers block audio playback until the user interacts with the page; the very first invincibility activation always succeeds (a key press triggered it), but in some browsers a deferred audio context creation is required.
- Mitigation: Pre-instantiate the HTMLAudioElement and call .play() in response to the first keydown to satisfy autoplay policies.

### No vulnerability scanning

- Evidence: No requirements lockfile, no Snyk / Dependabot configuration found in the file inventory.
- Impact: pygame transitive dependencies are not monitored.
- Mitigation: Acceptable for the current scope; consider adding pip-audit or safety check as a manual step.

## 5b. Runtime defects shipping today (added round-2 enrichment)

These are defects that will crash or visibly break the game on first use. Triage takes priority over the maintenance items in section 3. Every entry is line-cited and confirmed by re-reading the source.

### snake_game_console.py does not even parse

- Evidence: lines 287 and 290-291 — `snake.move()` is inside the super-food-eat conditional rather than the per-tick branch, and `storm_phase_ticks -= 1` follows `if not paused and storm_active:` at the same indent level. `python -c "import snake_game_console"` raises `IndentationError`.
- Impact: the entire Console implementation is dead today.
- Mitigation: outdent `snake.move()` to the per-tick branch (line 287) and indent `storm_phase_ticks -= 1` to be the body of its `if` (line 291). See `risk.md` section 5b.

### snake_game.py crashes on first super-food spawn

- Evidence: line 551 references `SUPER_FOOD_COLOR_A` which is not defined anywhere in the repo (verified by `Grep`). Pygame's main loop has no `try/except` around the draw call, so the game terminates.
- Impact: the Invincibility Power-Up feature on Pygame fails the moment the player approaches its first activation.
- Mitigation: add `SUPER_FOOD_COLOR_A = (255, 255, 0)` (or the team's intended yellow) alongside `SUPER_FOOD_COLOR_B` on line 49.

### snake_game.py crashes if pause is ever invoked

- Evidence: line 477 calls `draw_pause_overlay(screen)`; no `def draw_pause_overlay` anywhere.
- Impact: dormant defect — only triggers if `paused` is ever set to True. No key binding sets it today, so the crash is latent until a pause keybinding is added.
- Mitigation: implement the function (mirroring the Tkinter / HTML pause overlay) or remove the call until pause is delivered.

### snake_game_tkinter.py ships pause and rules screens that nothing invokes

- Evidence: `def toggle_pause` (line 513) has no `<KeyPress-p>` binding in the `__init__` keymap (lines 169-174). `def _draw_rules` (line 521) has no call site. `self.show_rules = True` (line 166) is initialised but never read (verified by `Grep` of `show_rules` in the file).
- Impact: feature gap, not a crash. The pause and how-to-play splash are visible only by reading the source.
- Mitigation: bind `<KeyPress-p>` to `self.toggle_pause` and call `self._draw_rules` from the initial canvas setup or from a help key.

### snake_game.py rules splash defined but never drawn

- Evidence: `def draw_rules_screen(screen):` at line 208 (lines 208-233 render the "Test1 Rules" splash and call `pygame.display.flip()`). `show_rules = True` is initialised in `main()` at line 268 and dismissed in the event handler at lines 276-279, but the draw block (lines 456-479) never calls `draw_rules_screen(screen)` (verified by `Grep`).
- Impact: the splash never appears; the `show_rules` mechanism silently swallows the first key press. This is the Pygame analogue of the Tkinter `_draw_rules` defect. See `risk.md` section 5b.
- Mitigation: add `if show_rules: draw_rules_screen(screen); continue` to the draw block, or remove the dead code.

### snake_game.py Mine Detonation Storm phase machine is mis-nested

- Evidence: `snake_game.py` lines 382-399. The `if storm_queue: ... else: ...` block at lines 388-399 is indented one level deeper than the `elif storm_phase == 'explosion':` at line 378, placing it inside the `for dy in range(-1, 2):` inner blast-cell loop rather than after it. Verified by line read. The mis-nested block reads:

  ```
  if storm_queue:
      storm_current_mine = storm_queue.pop(0)
      storm_phase = 'warning'
      storm_phase_elapsed = 0.0
      storm_warning_flash_acc = 0.0
      storm_warning_flash_index = 0
  else:
      storm_active = False
      storm_phase = None
      storm_current_mine = None
      storm_phase_elapsed = 0.0
      border_flash_state = False
  ```

  The block is intended to run **once** when `storm_phase == 'explosion'` and `storm_phase_elapsed >= EXPLOSION_DURATION`. Instead, because it is indented inside the `for dy` loop, it runs on every iteration of the inner blast-cell loop — and there is no `elapsed`-time guard at this location either.
- Impact: during the explosion phase the storm queue is popped repeatedly within a single tick; the phase is reset to `'warning'` while still inside the explosion-rendering branch, and `storm_phase_elapsed` is reset before any time has actually passed. The MDS state machine misbehaves the first time it reaches the explosion phase on the Pygame runtime.
- Mitigation: outdent lines 388-399 one level so they execute once per explosion frame (after the `for dy` loop has completed) and gate them on `storm_phase_ticks_elapsed >= EXPLOSION_DURATION` if the team wants an explosion to persist for the configured duration.

### snake_game.html depends on non-strict-mode globals

- Evidence: `paused` and `showRules` are assigned at lines 344, 386, 737 with no declaration. `Grep` finds zero `let|const|var` declarations.
- Impact: today the game runs because non-strict-mode browsers auto-create `window.paused` and `window.showRules`. If the file is ever loaded as a module (`type="module"`) strict mode is implicit and every read becomes `ReferenceError`.
- Mitigation: declare both with `let` at the top of the script block.

### Documentation now contradicts source for food and snake colours

- Evidence: `README.md` lines 60-61 / 67-68 state snake is blue and food is yellow. Source contradicts both. `risk.md` section 5b enumerates the four divergent food colour values across the four runtimes.
- Impact: any new contributor pattern-matching on the README will set the wrong constant and re-introduce the inconsistency.
- Mitigation: rewrite the colour section of README.md to say "snake colour cycles through an 8-entry palette on every food eaten" and to state each runtime's distinct food colour, or unify the food colour back to one value and update the docs.

## 5c. Defect coverage gaps (why these defects escaped review)

Round-2 audit found that the runtime defects in section 5b shipped because the test suite does not exercise the affected code paths. Captured for traceability so future test work can target the gaps:

- No automated test exercises the Pygame draw path; defects 1.1 (`SUPER_FOOD_COLOR_A`), 1.2 (`draw_pause_overlay`), and 1.3 (rules splash never drawn) escaped review precisely because no rendering pipeline is hit by the test suite.
- No automated test exercises the Pygame storm phase machine; the §5b storm mis-indent defect escaped review for the same reason.
- No automated test imports `snake_game_console.py`; the `IndentationError` escaped review because the file is never imported by any test or smoke check.
- No automated test exercises any Tkinter key-binding; the unreachable `toggle_pause` / `_draw_rules` defects escaped review for the same reason.
- No linter / `ast.parse` step is part of the workflow; running `python -m py_compile snake_game.py snake_game_tkinter.py snake_game_console.py` would have surfaced the console `IndentationError` immediately. The Pygame `NameError`s sit inside function bodies (name-resolution at call time) and the storm mis-indent is a valid but mis-nested block, so `py_compile` would not flag them — they require an actual run-through or a behavioural test of the storm pipeline.
- The `.pytest_cache/v/cache/nodeids` file contains historical node IDs that no longer exist in the current source (`test_calculate_score_happy_path`, `test_validate_name_accepts_three_char_alphanumeric`, others). The test suite was refactored at some point; the cache is harmlessly stale and would be rebuilt on the next `pytest` run.

### Stale standalone script: `verify_color.py`

- Reads `snake_game.py` as text, extracts `FOOD_COLOR`, prints the value and a "PASS / FAIL" message comparing it to `(100, 200, 255)` (light blue).
- Source actually contains `(255, 255, 255)`. The script therefore always prints "WRONG" against a true-positive value.
- Also prints an "average brightness" stat and a "may appear whitish" warning above brightness 200 — a relic of the era when the team was tuning the light-blue food.
- Not a test (no `unittest`, no `pytest`); will never fail a CI run, only the operator's interpretation of its stdout.
- `test_food_color.py` (the regex-based unittest) asserts the new white value, so the two artefacts disagree about ground truth.

## 6. Mitigation Strategy Summary (priority-ordered)

1. **(NEW, highest priority)** Fix the `IndentationError` in `snake_game_console.py` at lines 287 and 290-291. The Console implementation does not run at all today.
2. **(NEW)** Define `SUPER_FOOD_COLOR_A` next to `SUPER_FOOD_COLOR_B` in `snake_game.py` (line 49) so the Pygame super-food does not crash the loop on first flash.
3. **(NEW)** Outdent the storm-phase transition block at `snake_game.py` lines 388-399 so it executes once per explosion frame rather than once per inner blast-cell iteration (see `risk.md` section 5b).
4. **(NEW)** Either implement `draw_pause_overlay` in `snake_game.py` or remove the call on line 477. (Latent until pause is bound.)
5. **(NEW)** Declare `paused` and `showRules` with `let` at the top of `snake_game.html`'s script block.
6. **(NEW)** Invoke `draw_rules_screen(screen)` from the Pygame draw block, or remove the dead `show_rules` state at line 268 (see `risk.md` section 5b).
7. **(NEW)** Bind a key to `toggle_pause` and invoke `_draw_rules` from the initial canvas setup in `snake_game_tkinter.py`, or remove the unreachable code (and the dead `self.show_rules` flag).
8. Replace the two hard-coded INVINCIBILITY_MUSIC_PATH absolute Windows paths with paths relative to __file__. (Gameplay-affecting on any non-original-developer machine.)
9. Guard import winsound and fall back to a no-op audio function so the Tkinter version can run on Linux and macOS.
10. Move test_leaderboard.py, test_snake_game_tkinter_display.py, and test_food_color.py into tests/ (or widen pytest.ini testpaths) so the full suite runs in one command.
11. Rewrite test_food_color.py to import snake_game and assert the FOOD_COLOR attribute directly instead of regex-parsing the source.
12. Replace os.system("cls") with an ANSI cursor-home sequence in the console implementation.
13. Make leaderboard.save_scores atomic via tmp+rename.
14. Add highscores.json to a .gitignore and ship an empty seed only.
15. Delete verify_color.py (or update its expected value); the script currently misleads.
16. Update README.md to remove the C:\cursor\snake_game stale instruction and use relative paths; correct the food/snake colour claims.
17. Update `run_pygame_version.bat` line 2 to drop the "light blue food" banner (see `risk.md` section 5b).
18. Remove .bak files in favour of git tags.
19. Consider extracting a runtime-agnostic core to eliminate the four-way hand-synchronisation of features.
20. Delete `STRUCTURE.md` at the repo root or rewrite it to match the current four-runtime topology — it currently mis-describes the repo (see Suggested Future Enhancements item 1 in `decisions.md`).
21. Consolidate the three Cursor/Roo rule files (`docs/.cursorrules`, `.cursor/rules/rules.mdc`, `.roo/rules/rules.md`) into one canonical source.

## 7. Cross-references

- `code.md` section 7 — function-level hazard register for every defect listed in section 5b (file:line citations).
- `code.md` section 4 plus `structure.md` — explain why none of the section-5b defects are detected by the current test suite, and propose the smoke tests that would have caught them.
- `decisions.md` ADR-018 / ADR-021 — historical context for AC-11 (bonus food must be GREEN) and the deviation that introduced the white/hot-pink food era.
