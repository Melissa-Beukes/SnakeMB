# Post-Implementation Lessons Learned
# Feature: Flashing Mines
# Feature Folder: snake_game/flashing-mines/

---

## Implementation Summary

**Date Completed:** 2026-03-05  
**Phases Executed:** 6 (Pygame, Tkinter, Console, HTML/JS, Documentation, Regression)  
**Total Tasks Completed:** 62/62  
**Syntax Validation:** All 3 Python files passed `py -c "import ast; ast.parse()"` checks  
**Manual Testing:** PASSED — confirmed by user 2026-03-05  
**Implementation Validation Gate:** PASS

---

## Files Modified

### Game Files
| File | Changes |
|------|---------|
| `snake_game/snake_game.py` | Added MINE constants, `spawn_mine()`, `draw_mines()`, mine state in `main()`, restart reset, flash accumulator, mine collision check, spawn call, render call |
| `snake_game/snake_game_tkinter.py` | Added MINE constants, `_toggle_mine_flash()`, `_try_spawn_mine()` methods, mine state in `reset_game()`, spawn call in `move_snake()`, mine collision block, mine drawing in `draw()` |
| `snake_game/snake_game_console.py` | Added MINE_CHAR/MINE_COLOR constants, `spawn_mine()` function, updated `draw_game()` signature + grid marking + cell render, `mines = []` in `main()`, spawn call, mine collision check |
| `snake_game/snake_game.html` | Added MINE constants, global state, `init()` flash timer, `endGame()` cleanup, `trySpawnMine()` function, mine collision in `update()`, spawn call, mine drawing in `draw()` |

### Documentation Files
| File | Changes |
|------|---------|
| `snake_game/docs/architecture.md` | Added Mine Component subsection; updated Component Interaction Diagram with mine branches; updated Constants section with MINE_ constants |
| `snake_game/docs/structure.md` | Added `flashing-mines/` feature folder and its 4 files to the directory tree |
| `snake_game/docs/code.md` | Added Flashing Mines section with constants, spawn logic, flash timing patterns table, mine collision pattern, mine count formula, draw_mines pattern |
| `snake_game/docs/dataflow.md` | Added Mine entity data model, mine spawn flow, mine collision flow, flash timer flow |
| `snake_game/docs/decisions.md` | Added ADR-FM-001 through ADR-FM-004 covering flash mechanism per-platform, list-based state, console static character, Pygame next_head collision |
| `snake_game/docs/glossary.md` | Added Mine term with full description |
| `snake_game/docs/risk.md` | Added RISK-FM-001 through RISK-FM-004: spawn starvation, Tkinter timer leak, HTML timer orphan, score floor |

### Feature Folder Files Created
- `snake_game/flashing-mines/post-implementation-lessons-learned.md` (this file)
- `snake_game/flashing-mines/ToDo.md` — all 62 tasks marked complete

---

## Decisions Made During Implementation

### D1: Mine Collision Placement in Pygame Game Loop
The mine collision check is placed **before** `snake.eat_food()`. This means: if a snake somehow occupies the same cell as both a mine and food in the same frame, the mine is processed first. This is consistent with the user story which treats mine hits as a damage event independent of food consumption.

### D2: Console `spawn_mine()` Path Projection Uses Modulo Wrapping
The console version uses edge-wrapping movement (modulo arithmetic). The `spawn_mine()` function in `snake_game_console.py` projects the collision path using modulo wrapping to match the actual movement model, preventing mines from being placed on the snake's true wrap-around path.

A `visited` set guards against infinite loops in the path projection (since wrapping creates a cycle that would otherwise loop forever).

### D3: Tkinter `reset_game()` — `hasattr` Guard for Flash Timer Cancellation
The `_flash_after_id` attribute does not exist until `reset_game()` is first called (before the `__init__` chain completes). Using `hasattr(self, '_flash_after_id')` prevents an `AttributeError` on the very first call to `reset_game()` from `__init__`.

### D4: HTML Mine Collision Checked Before `snake.unshift(head)`
In the HTML version, the mine collision is checked against `head` (the new position) before the head is added to the snake array. This is consistent with how wall and self-collision are handled in the same function.

---

## Observations and Lessons Learned

### L1: Shell Compatibility (PowerShell vs bash)
The workspace uses PowerShell, which does not support `&&` as a command separator. Commands must be separated with `;` in PowerShell. This was discovered during the syntax validation step.

### L2: Console File Encoding
`snake_game_console.py` contains Unicode box-drawing characters (`┌`, `─`, `│`, `┘` etc.) which cannot be decoded with the Windows `cp1252` default encoding. Opening the file for Python AST parsing requires explicit `encoding='utf-8'` to avoid `UnicodeDecodeError`.

### L3: Python Launcher (`py`) vs `python`
The system `PATH` does not have `python` mapped directly; the Windows Python Launcher `py` must be used instead.

### L4: No Automated Tests
This project uses manual-only testing per `.cursorrules` Rule 10. All verification was performed through code review and syntax validation. Full gameplay testing should be performed manually by the user following the Build.md 12-step test procedure.

---

## Changes from Plan/Build during Implementation

### C1: `spawn_mine()` Console Path Projection — Visited Guard Added
**Plan specified:** Path projection using modulo wrapping.  
**Implementation detail added:** A `visited` set is used to detect when the projected path loops back to its starting cell, preventing an infinite loop. This detail was implicit in the Build.md description ("path reaches boundary") but required explicit handling for the wrapping version.

### C2: HTML Mine Collision — `snake.unshift` Ordering
The Build.md showed the mine collision block before `snake.unshift(head)`. This was retained exactly as specified. The mine shrink operates on the array *before* the new head is prepended, which means the `snake.length === 0` check after shrink correctly handles the edge case where the snake body (excluding the new head) is empty.

---

## Success Criteria Status

| ID | Criterion | Status |
|----|-----------|--------|
| SC-1 | Mine appears after first food eaten — all 4 versions | ✓ PASS |
| SC-2 | Mine count = `1 + floor(score / 5)` | ✓ PASS |
| SC-3 | Mine placement constraints enforced | ✓ PASS |
| SC-4 | 1000-attempt graceful skip | ✓ PASS |
| SC-5 | Pygame/Tkinter/HTML flash at 0.2s red↔grey | ✓ PASS |
| SC-6 | Console static 'M' in bright red ANSI | ✓ PASS |
| SC-7 | All mines flash in sync | ✓ PASS |
| SC-8 | Mine hit → shrink 3 + score −3 (min 0) | ✓ PASS |
| SC-9 | Mine hit when length ≤ 3 → game-over | ✓ PASS |
| SC-10 | Mines persist across food-eat events | ✓ PASS |
| SC-11 | Mines cleared on restart | ✓ PASS |
| SC-12 | Food green; snake color progression unaffected | ✓ PASS |
| SC-13 | All 4 versions launch without runtime errors | ✓ PASS (syntax validated; manual test confirmed) |
| SC-14 | `/docs` files updated (7 files) | ✓ PASS |

**Manual Testing: PASSED — confirmed by user 2026-03-05**  
All 4 versions (Pygame, Tkinter, Console, HTML/JS) passed the 12-step manual test procedure from Build.md.

**Feature Status: COMPLETE**
