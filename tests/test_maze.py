"""
test_maze.py - Automated Unit Tests for Maze Representation & NumPy Operations
===============================================================================
Covers:
    - TEST 9: Invalid maze dimensions rejected safely.
    - TEST 10: Start and Goal cannot be placed inside walls.
    - TEST 11: Random maze generation returns a correctly shaped matrix.
    - Experiment 9: NumPy matrix properties, counts, and clone isolation.
"""

import unittest
import numpy as np
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from maze import Maze, LEGAL_ACTIONS


class TestMazeRepresentation(unittest.TestCase):
    """Test suite verifying Maze initialization, bounds, and NumPy calculations."""

    def test_test_9_invalid_dimensions_rejected(self):
        """TEST 9: Invalid maze dimensions are rejected safely."""
        with self.assertRaises(ValueError):
            Maze(rows=1, cols=5)
        with self.assertRaises(ValueError):
            Maze(rows=5, cols=0)
        with self.assertRaises(ValueError):
            Maze(rows=-4, cols=10)

    def test_test_10_start_and_goal_cannot_be_walls(self):
        """TEST 10: Start and Goal cannot be placed inside walls."""
        maze = Maze(rows=6, cols=6, start=(1, 1), goal=(4, 4))
        # Ensure initial cells are empty (0)
        self.assertEqual(maze.grid[1, 1], 0)
        self.assertEqual(maze.grid[4, 4], 0)

        # Attempt to set wall on start coordinate - should return False and keep cell 0
        success_start = maze.set_wall(1, 1, is_wall=True)
        self.assertFalse(success_start)
        self.assertEqual(maze.grid[1, 1], 0)

        # Attempt to set wall on goal coordinate - should return False and keep cell 0
        success_goal = maze.set_wall(4, 4, is_wall=True)
        self.assertFalse(success_goal)
        self.assertEqual(maze.grid[4, 4], 0)

        # Attempt to toggle start or goal
        self.assertFalse(maze.toggle_wall(1, 1))
        self.assertEqual(maze.grid[1, 1], 0)
        self.assertFalse(maze.toggle_wall(4, 4))
        self.assertEqual(maze.grid[4, 4], 0)

    def test_test_11_random_maze_generation_shape_and_values(self):
        """TEST 11: Random maze generation returns a correctly shaped matrix."""
        rows, cols = 12, 14
        maze = Maze(rows=rows, cols=cols)
        maze.generate_random(density=0.30, seed=123, guarantee_solvable=True)

        self.assertIsInstance(maze.grid, np.ndarray)
        self.assertEqual(maze.shape, (rows, cols))
        self.assertEqual(maze.grid.dtype, np.int8)

        # All values must strictly be 0 (empty) or 1 (wall)
        unique_vals = set(np.unique(maze.grid))
        self.assertTrue(unique_vals.issubset({0, 1}))

        # Start and Goal must be open
        self.assertEqual(maze.grid[maze.start[0], maze.start[1]], 0)
        self.assertEqual(maze.grid[maze.goal[0], maze.goal[1]], 0)

    def test_numpy_operations_analytics(self):
        """Verify Experiment 9 NumPy operations: total_cells, wall_count, open_count, wall_density."""
        maze = Maze(rows=8, cols=10)
        # Place 10 walls manually
        for c in range(10):
            maze.set_wall(2, c, is_wall=True)

        total = maze.total_cells()
        walls = maze.wall_count()
        opens = maze.open_count()
        density = maze.wall_density()

        self.assertEqual(total, 80)
        self.assertEqual(walls, 10)
        self.assertEqual(opens, 70)
        self.assertEqual(walls + opens, total)
        self.assertAlmostEqual(density, (10 / 80) * 100.0, places=2)

    def test_maze_clone_isolation(self):
        """Verify that clone() creates a true deep copy of the NumPy matrix."""
        original = Maze(rows=5, cols=5)
        cloned = original.clone()

        # Modify cloned maze
        cloned.set_wall(2, 2, is_wall=True)
        self.assertEqual(cloned.grid[2, 2], 1)
        # Original must remain unmutated
        self.assertEqual(original.grid[2, 2], 0)

    def test_preset_mazes(self):
        """Ensure handcrafted demonstration presets load without error and have valid dimensions."""
        for name, expected_shape in [
            ("demo_10x10", (10, 10)),
            ("demo_15x15", (15, 15)),
            ("demo_20x20", (20, 20)),
        ]:
            m = Maze.create_preset(name)
            self.assertEqual(m.shape, expected_shape)
            self.assertEqual(m.grid[m.start[0], m.start[1]], 0)
            self.assertEqual(m.grid[m.goal[0], m.goal[1]], 0)


if __name__ == "__main__":
    unittest.main()
