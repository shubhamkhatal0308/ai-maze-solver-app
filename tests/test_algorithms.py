"""
test_algorithms.py - Automated Unit Tests for DFS and BFS Search Engines
========================================================================
Covers:
    - TEST 1: BFS finds a valid shortest path in a simple open grid.
    - TEST 2: BFS finds the shortest path around a wall.
    - TEST 3: DFS finds a valid path in a solvable maze.
    - TEST 4: DFS and BFS both report no path for a disconnected maze.
    - TEST 5: Start equals Goal returns a valid zero-step path.
    - TEST 8: Original maze remains unchanged after searches.
    - TEST 12: BFS path length <= DFS path length whenever both find a path.
    - TEST 13: Node counters are non-negative and consistent with documented definition.
"""

import unittest
import numpy as np
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from maze import Maze
from algorithms import dfs, bfs, astar, validate_path


class TestSearchAlgorithms(unittest.TestCase):
    """Test suite validating DFS and BFS state space exploration."""

    def test_test_1_bfs_shortest_path_open_grid(self):
        """TEST 1: BFS finds a valid shortest path in a simple open grid."""
        maze = Maze(rows=5, cols=5, start=(0, 0), goal=(4, 4))
        # Manhattan distance between (0, 0) and (4, 4) is 4 + 4 = 8 steps
        result = bfs(maze)

        self.assertTrue(result.path_found)
        self.assertIsNotNone(result.path)
        self.assertEqual(result.path_length, 8)
        self.assertEqual(len(result.path), 9)

        is_valid, msg = validate_path(maze.grid, result.path, maze.start, maze.goal)
        self.assertTrue(is_valid, msg)

    def test_test_2_bfs_shortest_path_around_wall(self):
        """TEST 2: BFS finds the shortest path around a wall."""
        # 5x5 grid with a vertical wall blocking col 2 for rows 0 to 3
        # Gap is at (4, 2)
        maze = Maze(rows=5, cols=5, start=(0, 0), goal=(0, 4))
        for r in range(4):
            maze.set_wall(r, 2, is_wall=True)

        result = bfs(maze)
        self.assertTrue(result.path_found)

        # Expected shortest path must go down to row 4, pass col 2, and go back up to row 0
        # (0,0) -> (4,0) (4 steps) -> (4,4) (4 steps) -> (0,4) (4 steps) = 12 steps
        self.assertEqual(result.path_length, 12)

        is_valid, msg = validate_path(maze.grid, result.path, maze.start, maze.goal)
        self.assertTrue(is_valid, msg)

    def test_test_3_dfs_valid_path_solvable_maze(self):
        """TEST 3: DFS finds a valid path in a solvable maze."""
        maze = Maze.create_preset("demo_15x15")
        result = dfs(maze)

        self.assertTrue(result.path_found)
        self.assertIsNotNone(result.path)
        self.assertGreater(result.path_length, 0)

        is_valid, msg = validate_path(maze.grid, result.path, maze.start, maze.goal)
        self.assertTrue(is_valid, msg)

    def test_test_4_disconnected_maze_reports_no_path(self):
        """TEST 4: DFS and BFS both report no path for a disconnected maze."""
        maze = Maze(rows=6, cols=6, start=(0, 0), goal=(5, 5))
        # Build an impenetrable horizontal wall across row 3
        for c in range(6):
            maze.set_wall(3, c, is_wall=True)

        dfs_res = dfs(maze)
        bfs_res = bfs(maze)

        self.assertFalse(dfs_res.path_found)
        self.assertIsNone(dfs_res.path)
        self.assertIsNone(dfs_res.path_length)

        self.assertFalse(bfs_res.path_found)
        self.assertIsNone(bfs_res.path)
        self.assertIsNone(bfs_res.path_length)

    def test_test_5_start_equals_goal_zero_steps(self):
        """TEST 5: Start equals Goal returns a valid zero-step path."""
        coord = (2, 2)
        maze = Maze(rows=5, cols=5, start=coord, goal=coord)

        dfs_res = dfs(maze)
        bfs_res = bfs(maze)

        # DFS Verification
        self.assertTrue(dfs_res.path_found)
        self.assertEqual(dfs_res.path, [coord])
        self.assertEqual(dfs_res.path_length, 0)

        # BFS Verification
        self.assertTrue(bfs_res.path_found)
        self.assertEqual(bfs_res.path, [coord])
        self.assertEqual(bfs_res.path_length, 0)

        # Path validation
        valid_dfs, _ = validate_path(maze.grid, dfs_res.path, coord, coord)
        valid_bfs, _ = validate_path(maze.grid, bfs_res.path, coord, coord)
        self.assertTrue(valid_dfs)
        self.assertTrue(valid_bfs)

    def test_test_8_maze_immutability_during_searches(self):
        """TEST 8: The original maze remains unchanged after searches."""
        maze = Maze.create_preset("demo_15x15")
        grid_before = maze.grid.copy()

        # Run both searches multiple times
        dfs(maze)
        bfs(maze)
        dfs(maze)
        bfs(maze)

        self.assertTrue(np.array_equal(maze.grid, grid_before), "Search modified original maze matrix!")

    def test_test_12_bfs_optimality_compared_to_dfs(self):
        """
        TEST 12: BFS path length is less than or equal to DFS path length
        whenever both find a path on the same unweighted maze.
        """
        # Test on handcrafted demonstration maze
        demo_maze = Maze.create_preset("demo_15x15")
        dfs_res = dfs(demo_maze)
        bfs_res = bfs(demo_maze)

        self.assertTrue(dfs_res.path_found)
        self.assertTrue(bfs_res.path_found)
        self.assertLessEqual(bfs_res.path_length, dfs_res.path_length)

        # Test across multiple random solvable mazes
        for seed in [11, 22, 33, 44, 55]:
            m = Maze(rows=12, cols=12)
            m.generate_random(density=0.25, seed=seed, guarantee_solvable=True)
            d_res = dfs(m)
            b_res = bfs(m)
            if d_res.path_found and b_res.path_found:
                self.assertLessEqual(
                    b_res.path_length,
                    d_res.path_length,
                    f"BFS path ({b_res.path_length}) was longer than DFS ({d_res.path_length}) on seed {seed}!"
                )

    def test_test_13_node_counters_consistency(self):
        """
        TEST 13: Node counters are non-negative and consistent with the documented
        definition: states popped from the frontier and processed.
        """
        maze = Maze.create_preset("demo_15x15")
        dfs_res = dfs(maze)
        bfs_res = bfs(maze)

        self.assertGreater(dfs_res.nodes_explored, 0)
        self.assertGreater(bfs_res.nodes_explored, 0)

        # nodes_explored must match the length of exploration_order
        self.assertEqual(dfs_res.nodes_explored, len(dfs_res.exploration_order))
        self.assertEqual(bfs_res.nodes_explored, len(bfs_res.exploration_order))

        # nodes_explored cannot exceed total cells in the grid
        self.assertLessEqual(dfs_res.nodes_explored, maze.total_cells())
        self.assertLessEqual(bfs_res.nodes_explored, maze.total_cells())

    def test_astar_shortest_path_and_efficiency(self):
        """Verify A* search finds the optimal shortest path matching BFS, with valid path validation."""
        demo_maze = Maze.create_preset("demo_15x15")
        bfs_res = bfs(demo_maze)
        astar_res = astar(demo_maze)

        self.assertTrue(astar_res.path_found)
        self.assertIsNotNone(astar_res.path)
        # A* with admissible Manhattan heuristic must find the same optimal shortest path length as BFS
        self.assertEqual(astar_res.path_length, bfs_res.path_length)

        # Validate path
        is_valid, msg = validate_path(demo_maze.grid, astar_res.path, demo_maze.start, demo_maze.goal)
        self.assertTrue(is_valid, msg)

        # Disconnected maze
        blocked_maze = Maze(rows=5, cols=5, start=(0, 0), goal=(4, 4))
        for c in range(5):
            blocked_maze.set_wall(2, c, is_wall=True)
        blocked_res = astar(blocked_maze)
        self.assertFalse(blocked_res.path_found)
        self.assertIsNone(blocked_res.path)


if __name__ == "__main__":
    unittest.main()
