"""
maze.py - Maze Representation and NumPy Operations
===================================================
Artificial Intelligence Mini Project: AI Maze Solver & Route Visualizer
Experiment 1: State Space Search & State Representation
Experiment 9: NumPy Operations for Grid-Based Search Spaces

This module defines the Maze class representing the 2D search environment.
The grid is encoded as a 2D NumPy array:
    0 = Empty traversable cell
    1 = Impassable obstacle / wall

State Space Formulation:
    - State: (row, column) coordinate inside the grid boundaries.
    - Initial State: Start coordinate S = (s_row, s_col).
    - Goal State: Goal coordinate G = (g_row, g_col).
    - Actions: Legal cardinal moves -> Up (-1, 0), Right (0, 1), Down (1, 0), Left (0, -1).
    - Transition Model: Result(s, a) = (s.row + a.row, s.col + a.col).
    - Goal Test: Current state equals G: (s == G).
    - Path Cost: Step cost is uniform (1 step per orthogonal move).
"""

from typing import List, Optional, Set, Tuple
import numpy as np


# Legal orthogonal actions defined deterministically: Up, Right, Down, Left
LEGAL_ACTIONS: List[Tuple[int, int]] = [
    (-1, 0),  # Up
    (0, 1),   # Right
    (1, 0),   # Down
    (0, -1),  # Left
]


class Maze:
    """
    Encapsulates the 2D grid search environment using NumPy.

    Attributes:
        rows (int): Number of grid rows (must be >= 2).
        cols (int): Number of grid columns (must be >= 2).
        grid (np.ndarray): 2D NumPy array of dtype int8 (0 = empty, 1 = wall).
        start (Tuple[int, int]): Coordinate of the start state (row, col).
        goal (Tuple[int, int]): Coordinate of the goal state (row, col).
    """

    def __init__(
        self,
        rows: int = 15,
        cols: int = 15,
        start: Optional[Tuple[int, int]] = None,
        goal: Optional[Tuple[int, int]] = None,
        grid: Optional[np.ndarray] = None,
    ):
        """
        Initialize the maze with dimensions, start, goal, and an optional initial grid.
        """
        if rows < 2 or cols < 2:
            raise ValueError(f"Invalid maze dimensions ({rows}x{cols}). Minimum allowed dimension is 2x2.")

        self.rows: int = int(rows)
        self.cols: int = int(cols)

        if grid is not None:
            self._validate_grid_array(grid, self.rows, self.cols)
            self.grid: np.ndarray = np.array(grid, dtype=np.int8, copy=True)
        else:
            # Experiment 9: NumPy matrix creation
            self.grid = np.zeros((self.rows, self.cols), dtype=np.int8)

        # Default start: top-left corner (0, 0)
        self.start: Tuple[int, int] = start if start is not None else (0, 0)
        # Default goal: bottom-right corner (rows-1, cols-1)
        self.goal: Tuple[int, int] = goal if goal is not None else (self.rows - 1, self.cols - 1)

        self._validate_coordinate(self.start, "Start")
        self._validate_coordinate(self.goal, "Goal")

        # Ensure start and goal are open cells (0 = empty)
        self.grid[self.start[0], self.start[1]] = 0
        self.grid[self.goal[0], self.goal[1]] = 0

    @staticmethod
    def _validate_grid_array(arr: np.ndarray, expected_rows: int, expected_cols: int) -> None:
        """Validate that the input grid is a well-formed 2D NumPy array containing only 0 and 1."""
        if not isinstance(arr, np.ndarray):
            raise TypeError("Grid must be a NumPy ndarray.")
        if arr.ndim != 2:
            raise ValueError(f"Grid must be 2-dimensional, got {arr.ndim} dimensions.")
        if arr.shape != (expected_rows, expected_cols):
            raise ValueError(f"Grid shape {arr.shape} does not match expected ({expected_rows}, {expected_cols}).")
        # Experiment 9: NumPy membership validation
        unique_vals = np.unique(arr)
        if not np.all(np.isin(unique_vals, [0, 1])):
            raise ValueError(f"Grid contains invalid values: {unique_vals}. Only 0 (empty) and 1 (wall) are permitted.")

    def _validate_coordinate(self, coord: Tuple[int, int], name: str = "Coordinate") -> None:
        """Ensure a coordinate is inside the grid boundaries."""
        if not (isinstance(coord, (tuple, list)) and len(coord) == 2):
            raise TypeError(f"{name} must be a 2-element tuple of integers.")
        r, c = coord
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise ValueError(f"{name} {coord} is outside grid boundaries ({self.rows}x{self.cols}).")

    @property
    def shape(self) -> Tuple[int, int]:
        """Return the (rows, cols) shape of the maze."""
        return self.grid.shape

    # =========================================================================
    # Experiment 9: NumPy Numerical Operations & Matrix Analytics
    # =========================================================================

    def total_cells(self) -> int:
        """Total number of cells in the maze using NumPy .size property."""
        return int(self.grid.size)

    def wall_count(self) -> int:
        """Count total obstacle/wall cells using NumPy summation."""
        return int(np.sum(self.grid == 1))

    def open_count(self) -> int:
        """Count total traversable empty cells using NumPy summation."""
        return int(np.sum(self.grid == 0))

    def wall_density(self) -> float:
        """Calculate percentage of maze occupied by walls using NumPy mean."""
        return float(np.mean(self.grid == 1) * 100.0)

    def get_summary(self) -> dict:
        """Return a structured analytical dictionary of the maze state."""
        return {
            "dimensions": f"{self.rows}x{self.cols}",
            "total_cells": self.total_cells(),
            "wall_count": self.wall_count(),
            "open_count": self.open_count(),
            "wall_density_pct": round(self.wall_density(), 2),
            "start": self.start,
            "goal": self.goal,
        }

    # =========================================================================
    # State Space Navigation Helpers
    # =========================================================================

    def is_in_bounds(self, r: int, c: int) -> bool:
        """Check if (r, c) is within the grid."""
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_wall(self, r: int, c: int) -> bool:
        """Check if (r, c) is an impassable wall."""
        if not self.is_in_bounds(r, c):
            return True
        return bool(self.grid[r, c] == 1)

    def is_traversable(self, r: int, c: int) -> bool:
        """Check if (r, c) is a legal, open cell inside the grid."""
        return self.is_in_bounds(r, c) and bool(self.grid[r, c] == 0)

    def get_successors(self, state: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Generate valid successor states from current state using LEGAL_ACTIONS.
        Returns adjacent open cells in deterministic order: Up, Right, Down, Left.
        """
        r, c = state
        successors: List[Tuple[int, int]] = []
        for dr, dc in LEGAL_ACTIONS:
            nr, nc = r + dr, c + dc
            if self.is_traversable(nr, nc):
                successors.append((nr, nc))
        return successors

    # =========================================================================
    # Maze Modification & Wall Manipulation
    # =========================================================================

    def set_wall(self, r: int, c: int, is_wall: bool = True) -> bool:
        """
        Place or remove a wall at (r, c).
        Will not place a wall on Start or Goal coordinates.
        Returns True if modified, False otherwise.
        """
        if not self.is_in_bounds(r, c):
            return False
        coord = (r, c)
        if coord == self.start or coord == self.goal:
            return False
        self.grid[r, c] = 1 if is_wall else 0
        return True

    def toggle_wall(self, r: int, c: int) -> bool:
        """
        Toggle the cell between wall and open cell.
        Returns True if toggled, False if coordinate is Start or Goal.
        """
        if not self.is_in_bounds(r, c):
            return False
        coord = (r, c)
        if coord == self.start or coord == self.goal:
            return False
        self.grid[r, c] = 0 if self.grid[r, c] == 1 else 1
        return True

    def clear_walls(self) -> None:
        """Clear all walls, resetting grid to an open NumPy zero-matrix."""
        self.grid.fill(0)

    def set_start(self, r: int, c: int) -> bool:
        """Set new Start coordinate. Automatically clears any wall at that location."""
        if not self.is_in_bounds(r, c):
            return False
        self.start = (r, c)
        self.grid[r, c] = 0
        return True

    def set_goal(self, r: int, c: int) -> bool:
        """Set new Goal coordinate. Automatically clears any wall at that location."""
        if not self.is_in_bounds(r, c):
            return False
        self.goal = (r, c)
        self.grid[r, c] = 0
        return True

    def clone(self) -> "Maze":
        """
        Create a deep copy of the Maze instance, including an independent
        copy of the NumPy grid array. Prevents algorithm mutations.
        """
        return Maze(
            rows=self.rows,
            cols=self.cols,
            start=self.start,
            goal=self.goal,
            grid=self.grid.copy(),
        )

    # =========================================================================
    # Random Maze Generation & Presets
    # =========================================================================

    def generate_random(
        self,
        density: float = 0.28,
        seed: Optional[int] = None,
        guarantee_solvable: bool = True,
    ) -> None:
        """
        Generate random obstacles across the maze using NumPy.

        Args:
            density (float): Target wall fraction in range (0.0, 0.6).
            seed (Optional[int]): Random seed for reproducible generation.
            guarantee_solvable (bool): If True, carves a guaranteed clear path
                                      corridor between Start and Goal.
        """
        density = max(0.05, min(0.60, float(density)))
        rng = np.random.default_rng(seed)

        # Experiment 9: Random matrix generation with NumPy
        random_matrix = rng.random((self.rows, self.cols))
        self.grid = (random_matrix < density).astype(np.int8)

        # Start and Goal must always be open
        self.grid[self.start[0], self.start[1]] = 0
        self.grid[self.goal[0], self.goal[1]] = 0

        if guarantee_solvable:
            self._carve_guaranteed_corridor(rng)

    def _carve_guaranteed_corridor(self, rng: np.random.Generator) -> None:
        """
        Carve a winding corridor connecting Start to Goal to ensure solvability.
        Uses a randomized Manhattan walk from Start to Goal.
        """
        curr_r, curr_c = self.start
        goal_r, goal_c = self.goal
        self.grid[curr_r, curr_c] = 0

        max_steps = self.rows * self.cols * 2
        steps = 0

        while (curr_r, curr_c) != (goal_r, goal_c) and steps < max_steps:
            steps += 1
            candidates: List[Tuple[int, int]] = []

            # Prioritize moves that reduce distance to goal with 70% probability
            dr = goal_r - curr_r
            dc = goal_c - curr_c

            possible_moves: List[Tuple[int, int]] = []
            if dr > 0:
                possible_moves.append((1, 0))
            elif dr < 0:
                possible_moves.append((-1, 0))
            if dc > 0:
                possible_moves.append((0, 1))
            elif dc < 0:
                possible_moves.append((0, -1))

            if possible_moves and rng.random() < 0.75:
                # Move towards goal
                idx = int(rng.integers(0, len(possible_moves)))
                move = possible_moves[idx]
            else:
                # Explore an arbitrary orthogonal step
                idx = int(rng.integers(0, len(LEGAL_ACTIONS)))
                move = LEGAL_ACTIONS[idx]

            nr, nc = curr_r + move[0], curr_c + move[1]
            if self.is_in_bounds(nr, nc):
                curr_r, curr_c = nr, nc
                self.grid[curr_r, curr_c] = 0

        # Ensure goal is open
        self.grid[goal_r, goal_c] = 0

    @classmethod
    def create_preset(cls, preset_name: str = "demo_15x15") -> "Maze":
        """
        Factory method to generate handcrafted, predictable demonstration mazes.
        Ideal for viva presentations to showcase DFS vs BFS exploration differences.
        """
        if preset_name == "demo_15x15":
            return cls._build_demo_15x15()
        elif preset_name == "demo_10x10":
            return cls._build_demo_10x10()
        elif preset_name == "demo_20x20":
            return cls._build_demo_20x20()
        else:
            raise ValueError(f"Unknown preset name: {preset_name}")

    @classmethod
    def _build_demo_15x15(cls) -> "Maze":
        """
        A handcrafted 15x15 demonstration maze where:
        - BFS branches directly along a short central/diagonal corridor (path length ~28).
        - DFS plunges deep into a deceptive winding upper/right corridor (path length ~46+).
        Produces vivid, dramatic visual and analytical differences!
        """
        maze = cls(rows=15, cols=15, start=(0, 0), goal=(14, 14))
        # Clear base
        maze.grid.fill(0)

        # Handcrafted wall structure
        walls = [
            # Vertical barriers with strategic openings
            (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2),
            (2, 4), (3, 4), (4, 4), (5, 4), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4), (13, 4), (14, 4),
            (0, 6), (1, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (9, 6), (10, 6), (11, 6), (12, 6),
            (2, 8), (3, 8), (4, 8), (6, 8), (7, 8), (8, 8), (9, 8), (11, 8), (12, 8), (13, 8), (14, 8),
            (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (7, 10), (8, 10), (9, 10), (10, 10), (12, 10), (13, 10),
            (0, 12), (2, 12), (3, 12), (4, 12), (5, 12), (6, 12), (8, 12), (9, 12), (10, 12), (11, 12), (13, 12),
            # Horizontal connectors
            (4, 3), (8, 3), (6, 5), (10, 5), (3, 7), (9, 7), (5, 9), (11, 9), (7, 11), (2, 13), (8, 13)
        ]
        for r, c in walls:
            if 0 <= r < 15 and 0 <= c < 15:
                maze.grid[r, c] = 1

        # Safeguard start and goal
        maze.grid[0, 0] = 0
        maze.grid[14, 14] = 0
        return maze

    @classmethod
    def _build_demo_10x10(cls) -> "Maze":
        """Compact 10x10 demonstration maze."""
        maze = cls(rows=10, cols=10, start=(0, 0), goal=(9, 9))
        walls = [
            (1, 1), (2, 1), (3, 1), (4, 1), (6, 1), (7, 1), (8, 1),
            (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (8, 3), (9, 3),
            (0, 5), (2, 5), (3, 5), (4, 5), (6, 5), (7, 5), (8, 5),
            (1, 7), (2, 7), (3, 7), (5, 7), (6, 7), (7, 7), (9, 7),
            (4, 2), (7, 4), (3, 6), (6, 8)
        ]
        for r, c in walls:
            maze.grid[r, c] = 1
        maze.grid[0, 0] = 0
        maze.grid[9, 9] = 0
        return maze

    @classmethod
    def _build_demo_20x20(cls) -> "Maze":
        """Full 20x20 demonstration maze."""
        maze = cls(rows=20, cols=20, start=(0, 0), goal=(19, 19))
        maze.generate_random(density=0.28, seed=42, guarantee_solvable=True)
        return maze
