"""
test_path_validation.py - Automated Tests for Path Validation & Chart Handling
==============================================================================
Covers:
    - TEST 6: Returned paths never cross walls.
    - TEST 7: Returned paths only contain legal adjacent moves.
    - TEST 14: Project modules import successfully.
    - TEST 15: Comparison results and charts handle the no-path case without crashing.
"""

import unittest
import numpy as np
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from maze import Maze
from algorithms import validate_path, dfs, bfs, compare_algorithms, SearchResult
from charts import create_comparison_figure, render_comparison_charts


class TestPathValidationAndCharts(unittest.TestCase):
    """Test suite for path integrity validation, import sanity, and chart safety."""

    def test_test_14_project_imports_successfully(self):
        """TEST 14: The project imports successfully when required dependencies are installed."""
        try:
            import maze
            import algorithms
            import visualization
            import charts
            import main
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import project modules: {e}")

    def test_test_6_returned_paths_never_cross_walls(self):
        """TEST 6: Returned paths never cross walls."""
        maze = Maze.create_preset("demo_15x15")
        dfs_res = dfs(maze)
        bfs_res = bfs(maze)

        self.assertTrue(dfs_res.path_found)
        self.assertTrue(bfs_res.path_found)

        # Verify no cell in either path is a wall
        for r, c in dfs_res.path:
            self.assertEqual(maze.grid[r, c], 0, f"DFS path crossed a wall at ({r}, {c})")

        for r, c in bfs_res.path:
            self.assertEqual(maze.grid[r, c], 0, f"BFS path crossed a wall at ({r}, {c})")

        # Now test that validate_path explicitly rejects a synthetic path that hits a wall
        synthetic_path = list(bfs_res.path)
        hit_coord = synthetic_path[len(synthetic_path) // 2]
        # Temporarily place a wall on that coordinate in a test grid
        test_grid = maze.grid.copy()
        test_grid[hit_coord[0], hit_coord[1]] = 1
        is_valid, msg = validate_path(test_grid, synthetic_path, maze.start, maze.goal)
        self.assertFalse(is_valid)
        self.assertIn("wall", msg.lower())

    def test_test_7_returned_paths_only_contain_legal_adjacent_moves(self):
        """TEST 7: Returned paths only contain legal adjacent moves (no diagonal or leap jumps)."""
        maze = Maze.create_preset("demo_15x15")
        for res in [dfs(maze), bfs(maze)]:
            for i in range(1, len(res.path)):
                r1, c1 = res.path[i - 1]
                r2, c2 = res.path[i]
                dr = abs(r2 - r1)
                dc = abs(c2 - c1)
                self.assertEqual(dr + dc, 1, f"Illegal jump between ({r1}, {c1}) and ({r2}, {c2})")

        # Test rejection of diagonal jump
        grid = np.zeros((5, 5), dtype=np.int8)
        diagonal_path = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        is_valid, msg = validate_path(grid, diagonal_path, (0, 0), (4, 4))
        self.assertFalse(is_valid)
        self.assertIn("invalid jump", msg.lower())

        # Test rejection of leap jump
        teleport_path = [(0, 0), (0, 1), (0, 4)]
        is_valid, msg = validate_path(grid, teleport_path, (0, 0), (0, 4))
        self.assertFalse(is_valid)
        self.assertIn("invalid jump", msg.lower())

    def test_test_15_comparison_and_charts_handle_no_path_case(self):
        """TEST 15: Comparison results and charts handle the no-path case safely."""
        # Create an unsolvable maze
        maze = Maze(rows=6, cols=6, start=(0, 0), goal=(5, 5))
        for c in range(6):
            maze.set_wall(2, c, is_wall=True)

        res_dfs, res_bfs, summary = compare_algorithms(maze)

        self.assertFalse(res_dfs.path_found)
        self.assertFalse(res_bfs.path_found)
        self.assertIsNone(res_dfs.path_length)
        self.assertIsNone(res_bfs.path_length)

        # Summary must indicate failure without throwing exceptions
        self.assertIn("unreachable", summary.lower())

        # Matplotlib chart rendering must handle None path_lengths without crashing
        fig = create_comparison_figure()
        try:
            render_comparison_charts(fig, res_dfs, res_bfs)
            # Verify the figure can be saved or rendered without error
            fig.canvas.draw()
        except Exception as e:
            self.fail(f"render_comparison_charts crashed on no-path case: {e}")

    def test_validate_path_endpoint_checks(self):
        """Verify that paths with wrong start or goal are rejected."""
        grid = np.zeros((4, 4), dtype=np.int8)
        path = [(0, 1), (0, 2), (0, 3)]
        # Wrong start
        is_valid, msg = validate_path(grid, path, (0, 0), (0, 3))
        self.assertFalse(is_valid)
        self.assertIn("begins at", msg.lower())

        # Wrong goal
        is_valid, msg = validate_path(grid, path, (0, 1), (3, 3))
        self.assertFalse(is_valid)
        self.assertIn("ends at", msg.lower())


if __name__ == "__main__":
    unittest.main()
