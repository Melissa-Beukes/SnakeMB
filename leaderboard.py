"""
High Score Leaderboard Manager
Pure business logic module for managing top 10 scores.
Implements persistent storage using JSON file format.
"""

import json
import os
from datetime import datetime, timezone


SCHEMA_VERSION = 2
VALID_NAME_MAX_LENGTH = 20


class HighScoreManager:
    """Manages high scores with persistent JSON storage."""

    def __init__(self, filepath='highscores.json'):
        """
        Initialize manager with file path.

        Args:
            filepath: Path to JSON file for storing scores
        """
        self.filepath = filepath

    def _default_stats(self):
        """Return default stats dict for new or migrated entries."""
        return {"food_eaten": 0, "mine_shrinks": 0, "invincibility_count": 0}

    def migrate_legacy_entries(self, entries):
        """Add default stats to legacy entries that lack stats fields.

        Args:
            entries: List of score dicts (may be missing stats fields)

        Returns:
            List of score dicts with stats fields guaranteed present.
            Entry's own values win over defaults (partial migration safe).
        """
        return [{**self._default_stats(), **e} for e in entries]

    def _unwrap_scores(self, raw):
        """Unwrap raw JSON data: extract scores list from v2 envelope or migrate legacy list."""
        if isinstance(raw, dict) and "scores" in raw:
            return raw["scores"]
        if isinstance(raw, list):
            return self.migrate_legacy_entries(raw)  # Auto-migrate legacy format
        return []

    def load_scores(self):
        """
        Load scores from JSON file. Auto-migrates legacy format to v2 on first load.

        Returns:
            List of score dictionaries (empty if file doesn't exist or corrupted)
        """
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)

            # Detect legacy bare list — migrate and persist v2 format
            if isinstance(data, list):
                migrated = self.migrate_legacy_entries(data)
                # One-time schema upgrade: persists v2 format on first load of legacy file
                self.save_scores(migrated)
                return migrated

            return self._unwrap_scores(data)
        except (json.JSONDecodeError, IOError):
            # Gracefully handle corrupted files or I/O errors
            return []

    def save_scores(self, scores):
        """
        Save scores to JSON file.

        Args:
            scores: List of score dictionaries to save

        Returns:
            True if save successful, False if I/O error occurred
        """
        try:
            with open(self.filepath, 'w') as f:
                # Write v2 envelope: {schema_version: 2, scores: [...]}
                json.dump({"schema_version": SCHEMA_VERSION, "scores": scores}, f, indent=2)
            return True
        except (IOError, OSError):
            # Gracefully handle disk full, permission errors, etc.
            return False

    def validate_name(self, name):
        """
        Validate player name (must be 1 to VALID_NAME_MAX_LENGTH alphanumeric characters).

        Args:
            name: Player name to validate

        Returns:
            True if valid (1 to VALID_NAME_MAX_LENGTH alphanumeric chars), False otherwise
        """
        return 1 <= len(name) <= VALID_NAME_MAX_LENGTH and name.isalnum()

    def is_high_score(self, score):
        """
        Check if score qualifies for top 10 leaderboard.

        Args:
            score: Score to check

        Returns:
            True if score qualifies, False otherwise
        """
        scores = self.load_scores()
        if len(scores) < 10:
            return True
        return score > scores[-1]['score']

    def add_score(self, score, name, food_eaten=0, mine_shrinks=0, invincibility_count=0):
        """
        Add new score to leaderboard.

        Args:
            score: Score value (integer)
            name: Player name (1 to VALID_NAME_MAX_LENGTH alphanumeric chars, converted to uppercase)
            food_eaten: Total food blocks consumed this game (default 0)
            mine_shrinks: Times snake shrunk from mine collision (default 0)
            invincibility_count: Times invincibility was activated (default 0)

        Returns:
            Updated list of top 10 scores

        Raises:
            ValueError: If name is invalid (not 1 to VALID_NAME_MAX_LENGTH alphanumeric characters)
        """
        # Validate name first
        if not self.validate_name(name):
            raise ValueError(
                f"Invalid name '{name}': must be 1-{VALID_NAME_MAX_LENGTH} alphanumeric characters"
            )

        scores = self.load_scores()

        # Create new entry with timestamp (UTC) and stats
        new_entry = {
            "score": score,
            "name": name.upper(),
            "date": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "food_eaten": food_eaten,
            "mine_shrinks": mine_shrinks,
            "invincibility_count": invincibility_count,
        }

        # Add to list
        scores.append(new_entry)

        # Sort descending by score
        scores.sort(key=lambda x: x['score'], reverse=True)

        # Keep only top 10
        scores = scores[:10]

        # Save to file (handle save failure gracefully)
        save_success = self.save_scores(scores)
        if not save_success:
            # If save fails, return original scores (don't persist the new score)
            return self.load_scores()

        return scores

    def get_leaderboard(self):
        """
        Get current leaderboard (top 10 scores).

        Returns:
            List of score dicts sorted descending by score. Each dict contains:
            score, name, date, food_eaten, mine_shrinks, invincibility_count.
        """
        return self.load_scores()
