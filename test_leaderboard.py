"""
Test suite for high score leaderboard system.
Uses temporary files to avoid permanent test artifacts.
Demonstrates pure Test-Driven Development (TDD).
"""

import unittest
import tempfile
import os
import json
from leaderboard import HighScoreManager


class TestLeaderboard(unittest.TestCase):
    """Test suite for HighScoreManager using temporary files."""
    
    def setUp(self):
        """Create temporary file for each test (isolated state)."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        self.manager = HighScoreManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary file after each test."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)


    # ========================================================================
    # TDD CYCLE 2: load_scores() - Empty File
    # ========================================================================
    
    def test_load_scores_from_empty_file_returns_empty_list(self):
        """Test that loading from non-existent file returns empty list."""
        scores = self.manager.load_scores()
        self.assertEqual(scores, [])
    
    # ========================================================================
    # TDD CYCLE 3: load_scores() - Valid File with Data
    # ========================================================================
    
    def test_load_scores_from_valid_file_returns_list(self):
        """Test that loading from valid JSON file returns score data."""
        # Write mock data to temp file
        mock_data = [
            {"score": 100, "name": "AAA", "date": "2026-04-20T10:00:00Z"},
            {"score": 50, "name": "BBB", "date": "2026-04-20T10:05:00Z"}
        ]
        with open(self.temp_file.name, 'w') as f:
            json.dump(mock_data, f)
        
        scores = self.manager.load_scores()
        self.assertEqual(len(scores), 2)
        self.assertEqual(scores[0]['score'], 100)
        self.assertEqual(scores[0]['name'], "AAA")
    
    # ========================================================================
    # TDD CYCLE 4: load_scores() - Corrupted File (Graceful Handling)
    # ========================================================================
    
    def test_load_scores_from_corrupted_file_returns_empty_list(self):
        """Test that corrupted JSON file is handled gracefully (returns empty list)."""
        # Write invalid JSON to temp file
        with open(self.temp_file.name, 'w') as f:
            f.write("INVALID JSON{{{")
        
        scores = self.manager.load_scores()
        self.assertEqual(scores, [])
    
    # ========================================================================
    # TDD CYCLE 5: save_scores() - Write Scores to File
    # ========================================================================
    
    def test_save_scores_writes_to_file(self):
        """Test that save_scores() writes data to JSON file correctly (v2 envelope)."""
        scores = [
            {"score": 100, "name": "AAA", "date": "2026-04-20T10:00:00Z"},
            {"score": 50, "name": "BBB", "date": "2026-04-20T10:05:00Z"}
        ]
        self.manager.save_scores(scores)
        
        # Verify file contains correct data (v2 envelope format)
        with open(self.temp_file.name, 'r') as f:
            loaded = json.load(f)
        self.assertEqual(loaded["scores"], scores)
    
    # ========================================================================
    # TDD CYCLE 6-10: validate_name() - Name Validation Rules
    # ========================================================================
    
    def test_validate_name_accepts_valid_alphanumeric(self):
        """Test that valid alphanumeric names of various lengths are accepted."""
        self.assertTrue(self.manager.validate_name("ABC"))       # 3 chars — backward compat
        self.assertTrue(self.manager.validate_name("A1B"))       # 3 chars mixed
        self.assertTrue(self.manager.validate_name("123"))       # 3 digits
        self.assertTrue(self.manager.validate_name("A"))         # 1 char — new minimum
        self.assertTrue(self.manager.validate_name("A" * 20))    # 20 chars — new maximum
    
    def test_validate_name_rejects_empty_name(self):
        """Test that empty string (0 characters) is rejected."""
        self.assertFalse(self.manager.validate_name(""))
    
    def test_validate_name_rejects_long_name(self):
        """Test that names longer than 20 characters are rejected."""
        self.assertFalse(self.manager.validate_name("A" * 21))
        self.assertFalse(self.manager.validate_name("A" * 25))
    
    def test_validate_name_rejects_special_chars(self):
        """Test that names with special characters are rejected."""
        self.assertFalse(self.manager.validate_name("A@B"))
        self.assertFalse(self.manager.validate_name("A-B"))
        self.assertFalse(self.manager.validate_name("A B"))
    
    def test_validate_name_rejects_empty_string(self):
        """Test that empty string is rejected."""
        self.assertFalse(self.manager.validate_name(""))
    
    # ========================================================================
    # TDD CYCLE 11-13: is_high_score() - Check if Score Qualifies
    # ========================================================================
    
    def test_is_high_score_returns_true_for_empty_leaderboard(self):
        """Test that any score qualifies for empty leaderboard."""
        self.assertTrue(self.manager.is_high_score(10))
        self.assertTrue(self.manager.is_high_score(1))
    
    def test_is_high_score_returns_true_for_partial_leaderboard(self):
        """Test that any score qualifies when leaderboard has < 10 entries."""
        # Create 5 scores
        scores = [
            {"score": 100 - i*10, "name": "AAA", "date": "2026-04-20T10:00:00Z"}
            for i in range(5)
        ]
        self.manager.save_scores(scores)
        
        self.assertTrue(self.manager.is_high_score(10))  # Any score qualifies
        self.assertTrue(self.manager.is_high_score(1))
    
    def test_is_high_score_returns_correctly_for_full_leaderboard(self):
        """Test score checking when leaderboard is full (10 entries)."""
        # Create 10 scores (100, 90, 80, ..., 10)
        scores = [
            {"score": 100 - i*10, "name": "AAA", "date": "2026-04-20T10:00:00Z"}
            for i in range(10)
        ]
        self.manager.save_scores(scores)
        
        # Score above lowest (10) should qualify
        self.assertTrue(self.manager.is_high_score(15))
        self.assertTrue(self.manager.is_high_score(11))
        
        # Score equal to lowest should NOT qualify
        self.assertFalse(self.manager.is_high_score(10))
        
        # Score below lowest should NOT qualify
        self.assertFalse(self.manager.is_high_score(5))
        self.assertFalse(self.manager.is_high_score(1))
    
    # ========================================================================
    # TDD CYCLE 14-17: add_score() - Add Score with Sorting & Limits
    # ========================================================================
    
    def test_add_score_to_empty_leaderboard(self):
        """Test adding first score to empty leaderboard."""
        result = self.manager.add_score(100, "AAA")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['score'], 100)
        self.assertEqual(result[0]['name'], "AAA")
        self.assertIn('date', result[0])
    
    def test_add_score_maintains_sorted_order(self):
        """Test that scores are sorted in descending order."""
        self.manager.add_score(100, "AAA")
        self.manager.add_score(50, "BBB")
        self.manager.add_score(150, "CCC")
        
        scores = self.manager.load_scores()
        self.assertEqual(scores[0]['score'], 150)
        self.assertEqual(scores[1]['score'], 100)
        self.assertEqual(scores[2]['score'], 50)
    
    def test_add_score_maintains_max_ten_entries(self):
        """Test that leaderboard maintains maximum 10 entries."""
        # Add 15 scores
        for i in range(15):
            self.manager.add_score(100 - i*5, f"A{i:02d}")
        
        scores = self.manager.load_scores()
        self.assertEqual(len(scores), 10)
        self.assertEqual(scores[0]['score'], 100)
        self.assertEqual(scores[-1]['score'], 55)  # 100 - 9*5
    
    def test_add_score_converts_name_to_uppercase(self):
        """Test that names are automatically converted to uppercase."""
        self.manager.add_score(100, "abc")
        
        scores = self.manager.load_scores()
        self.assertEqual(scores[0]['name'], "ABC")
    
    def test_add_score_includes_timestamp(self):
        """Test that scores include ISO 8601 timestamp."""
        self.manager.add_score(100, "AAA")
        
        scores = self.manager.load_scores()
        self.assertIn('date', scores[0])
        # Verify it's a non-empty string (ISO format validation would be overkill)
        self.assertTrue(len(scores[0]['date']) > 0)
    
    # ========================================================================
    # TDD CYCLE 18: get_leaderboard() - Retrieve Current Scores
    # ========================================================================
    
    def test_get_leaderboard_returns_current_scores(self):
        """Test that get_leaderboard() returns the current top scores."""
        self.manager.add_score(100, "AAA")
        self.manager.add_score(200, "BBB")
        
        scores = self.manager.get_leaderboard()
        self.assertEqual(len(scores), 2)
        self.assertEqual(scores[0]['score'], 200)
        self.assertEqual(scores[1]['score'], 100)
    
    # ========================================================================
    # CODE REVIEW FIX: Validate Names in add_score()
    # ========================================================================
    
    def test_add_score_rejects_invalid_name(self):
        """Test that add_score() rejects invalid names."""
        # Should raise ValueError for invalid names
        with self.assertRaises(ValueError):
            self.manager.add_score(100, "A" * 21)  # Too long (21 chars)
        
        with self.assertRaises(ValueError):
            self.manager.add_score(100, "")  # Empty — too short
        
        with self.assertRaises(ValueError):
            self.manager.add_score(100, "A@B")  # Special chars
        
        # Verify no scores were added
        scores = self.manager.get_leaderboard()
        self.assertEqual(len(scores), 0)
    
    # ========================================================================
    # CODE REVIEW FIX: save_scores() Error Handling
    # ========================================================================
    
    def test_save_scores_returns_false_on_io_error(self):
        """Test that save_scores() handles I/O errors gracefully."""
        # Create manager with invalid path (directory doesn't exist)
        invalid_manager = HighScoreManager("/invalid/path/that/does/not/exist/scores.json")
        
        scores = [{"score": 100, "name": "AAA", "date": "2026-04-20T10:00:00Z"}]
        result = invalid_manager.save_scores(scores)
        
        # Should return False on failure, not crash
        self.assertFalse(result)


class TestLeaderboardStatsV2(unittest.TestCase):
    """TDD Cycle tests for Leaderboard Stats Enhancement (HSL-002)."""

    def setUp(self):
        """Create temporary file for each test (isolated state)."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        self.manager = HighScoreManager(self.temp_file.name)

    def tearDown(self):
        """Clean up temporary file after each test."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    # ========================================================================
    # CYCLE 1: _default_stats() — Foundation Helper
    # ========================================================================

    def test_default_stats_helper_exists_and_returns_dict(self):
        """_default_stats() returns dict with food_eaten, mine_shrinks, invincibility_count all 0."""
        # Act
        result = self.manager._default_stats()

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result["food_eaten"], 0)
        self.assertEqual(result["mine_shrinks"], 0)
        self.assertEqual(result["invincibility_count"], 0)

    # ========================================================================
    # CYCLE 2: save_scores() writes schema_version 2 envelope
    # ========================================================================

    def test_save_scores_produces_schema_v2_envelope(self):
        """save_scores([]) writes a dict envelope with schema_version==2 and 'scores' key."""
        # Act
        self.manager.save_scores([])

        # Assert — read raw file
        with open(self.temp_file.name, 'r') as f:
            raw = json.load(f)

        self.assertIsInstance(raw, dict)
        self.assertEqual(raw["schema_version"], 2)
        self.assertIn("scores", raw)

    # ========================================================================
    # CYCLE 3: save_scores() empty list produces valid envelope
    # ========================================================================

    def test_save_scores_empty_list_produces_valid_envelope(self):
        """save_scores([]) produces envelope where 'scores' is an empty list."""
        # Act
        self.manager.save_scores([])

        # Assert
        with open(self.temp_file.name, 'r') as f:
            raw = json.load(f)

        self.assertEqual(raw["scores"], [])

    # ========================================================================
    # CYCLE 4: load_scores() reads v2 envelope
    # ========================================================================

    def test_load_scores_reads_v2_envelope(self):
        """load_scores() unwraps v2 envelope and returns inner scores list with all 6 fields."""
        # Arrange — write v2 envelope directly to file
        v2_data = {
            "schema_version": 2,
            "scores": [
                {
                    "score": 100, "name": "AAA", "date": "2026-05-06T12:00:00Z",
                    "food_eaten": 5, "mine_shrinks": 2, "invincibility_count": 1
                }
            ]
        }
        with open(self.temp_file.name, 'w') as f:
            json.dump(v2_data, f)

        # Act
        scores = self.manager.load_scores()

        # Assert
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["score"], 100)
        self.assertEqual(scores[0]["name"], "AAA")
        self.assertEqual(scores[0]["food_eaten"], 5)
        self.assertEqual(scores[0]["mine_shrinks"], 2)
        self.assertEqual(scores[0]["invincibility_count"], 1)

    # ========================================================================
    # CYCLE 5: load_scores() bare list does not crash
    # ========================================================================

    def test_load_scores_bare_list_does_not_crash(self):
        """load_scores() handles legacy bare-list JSON without exception, returns non-empty list."""
        # Arrange — write legacy bare list
        with open(self.temp_file.name, 'w') as f:
            f.write('[{"score": 100, "name": "AAA", "date": "2026-05-06T12:00:00Z"}]')

        # Act
        scores = self.manager.load_scores()

        # Assert
        self.assertIsInstance(scores, list)
        self.assertGreater(len(scores), 0)

    # ========================================================================
    # CYCLE 6: migrate_legacy_entries() adds default stats
    # ========================================================================

    def test_migrate_legacy_entries_adds_stats_defaults(self):
        """migrate_legacy_entries() adds default stats to entries missing those fields."""
        # Arrange
        entries = [{"score": 300, "name": "CCC", "date": "2026-05-06T12:00:00Z"}]

        # Act
        result = self.manager.migrate_legacy_entries(entries)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["food_eaten"], 0)
        self.assertEqual(result[0]["mine_shrinks"], 0)
        self.assertEqual(result[0]["invincibility_count"], 0)
        self.assertEqual(result[0]["score"], 300)
        self.assertEqual(result[0]["name"], "CCC")

    # ========================================================================
    # CYCLE 7: migrate_legacy_entries() does not overwrite existing stats
    # ========================================================================

    def test_migrate_does_not_overwrite_existing_stats(self):
        """migrate_legacy_entries() preserves stats fields already present in entry."""
        # Arrange — entry already has stats
        entries = [{
            "score": 200, "name": "BBB", "date": "2026-05-06T12:00:00Z",
            "food_eaten": 99, "mine_shrinks": 5, "invincibility_count": 3
        }]

        # Act
        result = self.manager.migrate_legacy_entries(entries)

        # Assert — existing values preserved, not overwritten to 0
        self.assertEqual(result[0]["food_eaten"], 99)
        self.assertEqual(result[0]["mine_shrinks"], 5)
        self.assertEqual(result[0]["invincibility_count"], 3)

    # ========================================================================
    # CYCLE 8: migrate_legacy_entries() preserves score/name/date
    # ========================================================================

    def test_migrate_preserves_score_name_date(self):
        """migrate_legacy_entries() preserves score, name, date fields unchanged."""
        # Arrange
        entries = [{"score": 450, "name": "AAA", "date": "2026-05-06T14:00:00Z"}]

        # Act
        result = self.manager.migrate_legacy_entries(entries)

        # Assert
        self.assertEqual(result[0]["score"], 450)
        self.assertEqual(result[0]["name"], "AAA")
        self.assertIn("date", result[0])

    # ========================================================================
    # CYCLE 9: load_scores() auto-migrates legacy list and returns defaults
    # ========================================================================

    def test_load_scores_migrates_legacy_and_returns_defaults(self):
        """load_scores() auto-migrates legacy bare list and returns entries with stats defaults."""
        # Arrange — write legacy bare list
        with open(self.temp_file.name, 'w') as f:
            f.write('[{"score": 100, "name": "AAA", "date": "2026-05-06T12:00:00Z"}]')

        # Act
        scores = self.manager.load_scores()

        # Assert — stats defaults added
        self.assertEqual(scores[0]["food_eaten"], 0)
        self.assertEqual(scores[0]["mine_shrinks"], 0)
        self.assertEqual(scores[0]["invincibility_count"], 0)

    # ========================================================================
    # CYCLE 10: load_scores() persists migration to file
    # ========================================================================

    def test_load_scores_persists_migration_to_file(self):
        """load_scores() persists v2 format to file after migrating legacy bare list."""
        # Arrange — write legacy bare list
        with open(self.temp_file.name, 'w') as f:
            f.write('[{"score": 100, "name": "AAA", "date": "2026-05-06T12:00:00Z"}]')

        # Act — load triggers migration
        self.manager.load_scores()

        # Assert — file now has v2 envelope
        with open(self.temp_file.name, 'r') as f:
            raw = json.load(f)

        self.assertIsInstance(raw, dict)
        self.assertEqual(raw["schema_version"], 2)

    # ========================================================================
    # CYCLE 11: add_score() accepts food_eaten, mine_shrinks, invincibility_count
    # ========================================================================

    def test_add_score_accepts_food_eaten_mine_shrinks_invincibility_count(self):
        """add_score() accepts food_eaten, mine_shrinks, invincibility_count kwargs and stores them."""
        # Act
        scores = self.manager.add_score(
            100, "AAA",
            food_eaten=10, mine_shrinks=3, invincibility_count=2
        )

        # Assert
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["food_eaten"], 10)
        self.assertEqual(scores[0]["mine_shrinks"], 3)
        self.assertEqual(scores[0]["invincibility_count"], 2)

    # ========================================================================
    # CYCLE 12: add_score() 2-arg call still works (backward compat)
    # ========================================================================

    def test_add_score_two_arg_call_still_works(self):
        """add_score(score, name) with no stats args defaults all stats to 0 (backward compat)."""
        # Act — old 2-arg call
        scores = self.manager.add_score(100, "AAA")

        # Assert
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["food_eaten"], 0)
        self.assertEqual(scores[0]["mine_shrinks"], 0)
        self.assertEqual(scores[0]["invincibility_count"], 0)

    # ========================================================================
    # CYCLE 13: add_score() stats written to file
    # ========================================================================

    def test_add_score_stats_written_to_file(self):
        """Stats passed to add_score() are persisted to JSON file."""
        # Act
        self.manager.add_score(200, "BBB", food_eaten=15, mine_shrinks=1, invincibility_count=3)

        # Assert — read raw file
        with open(self.temp_file.name, 'r') as f:
            raw = json.load(f)

        self.assertEqual(raw["scores"][0]["food_eaten"], 15)
        self.assertEqual(raw["scores"][0]["mine_shrinks"], 1)
        self.assertEqual(raw["scores"][0]["invincibility_count"], 3)

    # ========================================================================
    # CYCLE 14: full round-trip add/reload stats match
    # ========================================================================

    def test_full_roundtrip_add_reload_stats_match(self):
        """Stats added via add_score() survive full save/reload with a fresh manager instance."""
        # Arrange + Act — add score with stats
        self.manager.add_score(300, "AAA", food_eaten=77, mine_shrinks=4, invincibility_count=6)

        # Create fresh manager pointing to same file
        fresh_manager = HighScoreManager(self.temp_file.name)
        scores = fresh_manager.load_scores()

        # Assert — all stats match exactly
        self.assertEqual(scores[0]["food_eaten"], 77)
        self.assertEqual(scores[0]["mine_shrinks"], 4)
        self.assertEqual(scores[0]["invincibility_count"], 6)
        self.assertEqual(scores[0]["score"], 300)
        self.assertEqual(scores[0]["name"], "AAA")

    # ========================================================================
    # CYCLE 15: get_leaderboard() includes stats
    # ========================================================================

    def test_get_leaderboard_includes_stats(self):
        """get_leaderboard() returns entries with food_eaten, mine_shrinks, invincibility_count."""
        # Arrange
        self.manager.add_score(150, "ZZZ", food_eaten=20, mine_shrinks=2, invincibility_count=1)

        # Act
        leaderboard = self.manager.get_leaderboard()

        # Assert
        self.assertEqual(len(leaderboard), 1)
        self.assertIn("food_eaten", leaderboard[0])
        self.assertIn("mine_shrinks", leaderboard[0])
        self.assertIn("invincibility_count", leaderboard[0])
        self.assertEqual(leaderboard[0]["food_eaten"], 20)

    # ========================================================================
    # CYCLE 16: corrupted file returns empty list (regression)
    # ========================================================================

    def test_corrupted_file_returns_empty_list(self):
        """load_scores() returns [] gracefully when file contains invalid JSON."""
        # Arrange
        with open(self.temp_file.name, 'w') as f:
            f.write("{{INVALID JSON")

        # Act
        scores = self.manager.load_scores()

        # Assert
        self.assertEqual(scores, [])

    # ========================================================================
    # CYCLE 17: multiple legacy entries all get defaults
    # ========================================================================

    def test_multiple_legacy_entries_all_get_defaults(self):
        """load_scores() migrates all entries in a multi-entry legacy file."""
        # Arrange — 5-entry legacy bare list
        legacy_entries = [
            {"score": 100 - i * 10, "name": f"A{i:02d}", "date": "2026-05-06T12:00:00Z"}
            for i in range(5)
        ]
        with open(self.temp_file.name, 'w') as f:
            json.dump(legacy_entries, f)

        # Act
        scores = self.manager.load_scores()

        # Assert — all 5 entries migrated
        self.assertEqual(len(scores), 5)
        self.assertTrue(all(e["food_eaten"] == 0 for e in scores))
        self.assertTrue(all(e["mine_shrinks"] == 0 for e in scores))
        self.assertTrue(all(e["invincibility_count"] == 0 for e in scores))

    # ========================================================================
    # CYCLE 18: sort order unaffected by stats
    # ========================================================================

    def test_sort_order_unaffected_by_stats(self):
        """Leaderboard sort order is by score only; stats values do not affect ranking."""
        # Arrange — low score with huge food_eaten, high score with tiny food_eaten
        self.manager.add_score(50, "LOW", food_eaten=999, mine_shrinks=0, invincibility_count=0)
        self.manager.add_score(200, "HIG", food_eaten=1, mine_shrinks=0, invincibility_count=0)

        # Act
        leaderboard = self.manager.get_leaderboard()

        # Assert — sorted by score descending
        self.assertEqual(leaderboard[0]["score"], 200)
        self.assertEqual(leaderboard[1]["score"], 50)
        self.assertEqual(leaderboard[0]["name"], "HIG")

    # ========================================================================
    # CYCLE 19: zero stats not dropped
    # ========================================================================

    def test_zero_stats_not_dropped(self):
        """Stats with value 0 are preserved through save/load — not dropped or converted to None."""
        # Act
        self.manager.add_score(100, "AAA", food_eaten=0, mine_shrinks=0, invincibility_count=0)

        # Reload with fresh manager
        fresh_manager = HighScoreManager(self.temp_file.name)
        scores = fresh_manager.load_scores()

        # Assert — keys present, values are integer 0 (not None, not missing)
        self.assertIn("food_eaten", scores[0])
        self.assertEqual(scores[0]["food_eaten"], 0)
        self.assertIsNotNone(scores[0]["food_eaten"])
        self.assertIn("mine_shrinks", scores[0])
        self.assertEqual(scores[0]["mine_shrinks"], 0)
        self.assertIn("invincibility_count", scores[0])
        self.assertEqual(scores[0]["invincibility_count"], 0)

    # ========================================================================
    # CYCLE 20: migrate_legacy_entries() handles empty input
    # ========================================================================

    def test_migrate_empty_input_returns_empty_list(self):
        """migrate_legacy_entries([]) returns [] without error."""
        # Act
        result = self.manager.migrate_legacy_entries([])

        # Assert
        self.assertEqual(result, [])


class TestNameLengthBoundary(unittest.TestCase):
    """LNL-001: Name Length Boundary Tests (3 → 20 character limit increase)."""

    def setUp(self):
        """Create temporary file for each test (isolated state)."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.close()
        self.manager = HighScoreManager(self.temp_file.name)

    def tearDown(self):
        """Clean up temporary file after each test."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_validate_name_accepts_one_char_minimum_boundary(self):
        """Valid name — exactly 1 character (minimum boundary)."""
        self.assertTrue(self.manager.validate_name("A"))

    def test_validate_name_accepts_twenty_chars_maximum_boundary(self):
        """Valid name — exactly 20 characters (maximum boundary)."""
        self.assertTrue(self.manager.validate_name("A" * 20))

    def test_validate_name_rejects_twenty_one_chars_over_limit(self):
        """Invalid name — exactly 21 characters (just over new limit)."""
        self.assertFalse(self.manager.validate_name("A" * 21))

    def test_validate_name_mixed_case_stored_as_uppercase(self):
        """Valid name — mixed-case input is converted to uppercase on storage."""
        result = self.manager.add_score(100, "abcde")
        self.assertEqual(result[0]['name'], "ABCDE")

    def test_validate_name_rejects_empty_string_still_rejected(self):
        """Invalid name — empty string still rejected under new limit."""
        self.assertFalse(self.manager.validate_name(""))


if __name__ == '__main__':
    unittest.main()
