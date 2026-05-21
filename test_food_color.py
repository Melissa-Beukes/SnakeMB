"""
Test for white food color feature in snake_game.py (Pygame version).

This test verifies that FOOD_COLOR constant is set to white (255, 255, 255).
This is a COLOR-ONLY change with no gameplay modifications.

This test parses the source file directly to avoid pygame import issues.
"""

import unittest
import os
import re


class TestFoodColor(unittest.TestCase):
    """Test that food color is white in Pygame version."""
    
    def setUp(self):
        """Read the snake_game.py source file."""
        self.source_file = os.path.join(os.path.dirname(__file__), 'snake_game.py')
        with open(self.source_file, 'r', encoding='utf-8') as f:
            self.source_code = f.read()
    
    def test_food_color_is_white(self):
        """
        FOOD_COLOR constant should be white (255, 255, 255).
        
        This verifies the cosmetic color change from light blue to white.
        No gameplay logic should be affected by this change.
        """
        expected_color = (255, 255, 255)  # White
        
        # Parse FOOD_COLOR from source
        match = re.search(r'FOOD_COLOR\s*=\s*\((\d+),\s*(\d+),\s*(\d+)\)', self.source_code)
        
        self.assertIsNotNone(match, "Could not find FOOD_COLOR constant in snake_game.py")
        
        actual_color = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        
        self.assertEqual(
            actual_color,
            expected_color,
            f"FOOD_COLOR should be white {expected_color}, but got {actual_color}"
        )
    
    def test_food_color_is_not_yellow(self):
        """
        FOOD_COLOR should NOT be yellow (255, 255, 0).
        
        This confirms we've moved away from the old yellow color.
        """
        old_yellow_color = (255, 255, 0)
        
        # Parse FOOD_COLOR from source
        match = re.search(r'FOOD_COLOR\s*=\s*\((\d+),\s*(\d+),\s*(\d+)\)', self.source_code)
        
        self.assertIsNotNone(match, "Could not find FOOD_COLOR constant in snake_game.py")
        
        actual_color = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        
        self.assertNotEqual(
            actual_color,
            old_yellow_color,
            f"FOOD_COLOR should not be yellow {old_yellow_color}"
        )
    
    def test_food_color_comment_mentions_white(self):
        """
        Comment for FOOD_COLOR should mention 'white'.
        
        This ensures documentation matches implementation.
        """
        # Find the FOOD_COLOR line with comment
        match = re.search(r'FOOD_COLOR\s*=\s*\([^)]+\)\s*#\s*(.+)', self.source_code)
        
        self.assertIsNotNone(match, "Could not find FOOD_COLOR constant with comment")
        
        comment = match.group(1).lower()
        
        self.assertIn(
            'white',
            comment,
            f"FOOD_COLOR comment should mention 'white', but got: {comment}"
        )


if __name__ == '__main__':
    unittest.main()
