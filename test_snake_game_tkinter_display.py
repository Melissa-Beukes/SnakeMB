"""Test suite for AC-6 leaderboard stats display.

Validates the pure formatter helper and the SnakeGame integration
that wires it to messagebox.showinfo. Uses unittest to match
test_leaderboard.py conventions; no real Tk root is constructed.
"""

import json
import os
import tempfile
import unittest
from unittest import mock


NEW_ENTRY = {
    "score": 450, "name": "AAA", "date": "2026-05-06T14:00:00Z",
    "food_eaten": 85, "mine_shrinks": 5, "invincibility_count": 3,
}
LEGACY_ENTRY = {
    "score": 100, "name": "OLD", "date": "2026-04-01T10:00:00Z",
}
MIXED_ENTRIES = [NEW_ENTRY, LEGACY_ENTRY]
HEADER_TOKENS = ["Rank", "Name", "Score", "Food", "Mines", "Inv"]


def _body_text(msg):
    """Strip the title line so digit-collision false positives are avoided."""
    return "\n".join(
        line for line in msg.splitlines()
        if "TOP 10 HIGH SCORES" not in line
    )


def _make_game(leaderboard, score=0):
    """Build a partial SnakeGame without invoking __init__ (no Tk root)."""
    from snake_game_tkinter import SnakeGame
    game = SnakeGame.__new__(SnakeGame)
    game.leaderboard = leaderboard
    game.root = mock.MagicMock()
    game.score = score
    return game


class TestFormatLeaderboardMessage(unittest.TestCase):
    """Pure-function tests for format_leaderboard_message."""

    def test_format_callable_with_empty_list_does_not_raise(self):
        from snake_game_tkinter import format_leaderboard_message
        self.assertTrue(callable(format_leaderboard_message))
        result = format_leaderboard_message([])
        self.assertIsInstance(result, str)

    def test_format_empty_list_contains_no_high_scores_text(self):
        from snake_game_tkinter import format_leaderboard_message
        result = format_leaderboard_message([])
        self.assertIn("No high scores yet!", result)

    def test_format_nonempty_contains_title(self):
        from snake_game_tkinter import format_leaderboard_message
        result = format_leaderboard_message([NEW_ENTRY])
        self.assertIn("TOP 10 HIGH SCORES", result)

    def test_format_nonempty_contains_all_six_column_tokens(self):
        from snake_game_tkinter import format_leaderboard_message
        result = format_leaderboard_message([NEW_ENTRY]).lower()
        for token in HEADER_TOKENS:
            self.assertIn(token.lower(), result, msg=f"missing token: {token}")

    def test_format_row_contains_name_and_score(self):
        from snake_game_tkinter import format_leaderboard_message
        result = format_leaderboard_message([NEW_ENTRY])
        self.assertIn("AAA", result)
        self.assertIn("450", result)

    def test_format_row_contains_all_stats_values(self):
        from snake_game_tkinter import format_leaderboard_message
        result = format_leaderboard_message([NEW_ENTRY])
        body = _body_text(result)
        self.assertIn("85", body)
        self.assertIn("5", body)
        self.assertIn("3", body)

    def test_format_legacy_entry_does_not_raise_and_shows_zero(self):
        from snake_game_tkinter import format_leaderboard_message
        result = format_leaderboard_message([LEGACY_ENTRY])
        self.assertIn("OLD", result)
        self.assertIn("100", result)
        self.assertIn("0", result)

    def test_format_multiple_entries_all_present(self):
        from snake_game_tkinter import format_leaderboard_message
        entries = [
            {**NEW_ENTRY, "name": "AAA", "score": 300},
            {**NEW_ENTRY, "name": "BBB", "score": 200},
            {**NEW_ENTRY, "name": "CCC", "score": 100},
        ]
        result = format_leaderboard_message(entries)
        self.assertIn("AAA", result)
        self.assertIn("BBB", result)
        self.assertIn("CCC", result)

    def test_format_mixed_legacy_and_new_entries_render(self):
        from snake_game_tkinter import format_leaderboard_message
        result = format_leaderboard_message(MIXED_ENTRIES)
        self.assertIn("AAA", result)
        self.assertIn("OLD", result)
        self.assertIn("0", result)


class TestDisplayIntegration(unittest.TestCase):
    """Integration tests for SnakeGame.display_leaderboard.

    The display pipeline is: display_leaderboard -> format_leaderboard_message
    -> _show_leaderboard_window (Toplevel + monospace Text). Tests patch
    the window helper and assert on its captured message arg, so no real
    Tk root is constructed.
    """

    def setUp(self):
        self.patcher = mock.patch(
            "snake_game_tkinter._show_leaderboard_window"
        )
        self.mock_show = self.patcher.start()
        tf = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        )
        tf.close()
        self.tmp_path = tf.name

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.tmp_path):
            os.unlink(self.tmp_path)

    def _captured_message(self):
        """Return the `message` arg passed to _show_leaderboard_window."""
        self.assertEqual(self.mock_show.call_count, 1)
        args, kwargs = self.mock_show.call_args
        if "message" in kwargs:
            return kwargs["message"]
        return args[1]

    def test_display_leaderboard_passes_formatter_output_to_window(self):
        from snake_game_tkinter import (
            SnakeGame, format_leaderboard_message,
        )
        stub_leaderboard = mock.MagicMock()
        stub_leaderboard.get_leaderboard.return_value = MIXED_ENTRIES
        game = _make_game(stub_leaderboard)

        SnakeGame.display_leaderboard(game)

        self.assertEqual(
            self._captured_message(),
            format_leaderboard_message(MIXED_ENTRIES),
        )

    def test_display_leaderboard_empty_shows_empty_state_message(self):
        from snake_game_tkinter import SnakeGame
        stub_leaderboard = mock.MagicMock()
        stub_leaderboard.get_leaderboard.return_value = []
        game = _make_game(stub_leaderboard)

        SnakeGame.display_leaderboard(game)

        self.assertIn("No high scores yet!", self._captured_message())

    def test_handle_game_over_e2e_shows_stats_columns_for_mixed_file(self):
        from leaderboard import HighScoreManager
        from snake_game_tkinter import SnakeGame

        legacy = [
            {"score": 100 - i * 10, "name": f"L{i:02d}",
             "date": "2026-04-01T10:00:00Z"}
            for i in range(9)
        ]
        new = {
            "score": 5, "name": "NEW",
            "date": "2026-05-01T10:00:00Z",
            "food_eaten": 7, "mine_shrinks": 1, "invincibility_count": 2,
        }
        with open(self.tmp_path, "w") as f:
            json.dump(
                {"schema_version": 2, "scores": legacy + [new]}, f
            )

        manager = HighScoreManager(self.tmp_path)
        game = _make_game(manager, score=0)

        SnakeGame.handle_game_over(game)

        captured = self._captured_message()
        self.assertIn("food", captured.lower())
        self.assertIn("mines", captured.lower())
        self.assertIn("inv", captured.lower())
        for name in [f"L{i:02d}" for i in range(9)] + ["NEW"]:
            self.assertIn(name, captured)
        self.assertIn("0", captured)


if __name__ == "__main__":
    unittest.main()
