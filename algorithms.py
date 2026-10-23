"""
algorithms.py - State Space Search Algorithms & Path Validation
================================================================
Artificial Intelligence Mini Project: AI Maze Solver & Route Visualizer
Experiment 4: Depth First Search (DFS) Implementation
Experiment 5: Breadth First Search (BFS) Implementation

This module provides from-scratch implementations of DFS and BFS,
deterministic path reconstruction, path validation, and empirical
performance measurement using time.perf_counter().

Consistent Definition of "Nodes Explored":
    The total number of unique states removed (popped) from the search
    frontier (stack for DFS, queue for BFS) and expanded/processed.
"""

from collections import deque
from dataclasses import dataclass
import heapq
import time
from typing import Dict, List, Optional, Set, Tuple
import numpy as np

from maze import LEGAL_ACTIONS, Maze


@dataclass
class SearchResult:
    """
    Standardized result structure returned by search algorithms.

    Attributes:
        algorithm (str): Name of the algorithm ('DFS' or 'BFS').
        path_found (bool): True if a continuous path from start to goal exists.
        path (Optional[List[Tuple[int, int]]]): Sequence of coordinates from start to goal.
        nodes_explored (int): Number of states popped from the frontier and processed.
        path_length (Optional[int]): Number of steps (len(path) - 1), or None if no path.
        execution_time_ms (float): Pure algorithm computation time in milliseconds.
        exploration_order (List[Tuple[int, int]]): Order in which cells were expanded.
        status_message (str): Explanatory summary of the search outcome.
    """
    algorithm: str
    path_found: bool
    path: Optional[List[Tuple[int, int]]]
    nodes_explored: int
    path_length: Optional[int]
    execution_time_ms: float
    exploration_order: List[Tuple[int, int]]
    status_message: str


def validate_path(
    grid: np.ndarray,
    path: Optional[List[Tuple[int, int]]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
) -> Tuple[bool, str]:
    """
    Validate a search path against the maze rules.

    Requirements verified:
        1. Path is not None and not empty.
        2. Path begins at the designated Start coordinate.
        3. Path ends at the designated Goal coordinate.
        4. Every path cell is inside grid boundaries.
        5. No path cell is a wall (grid value == 1).
        6. Consecutive cells are adjacent by exactly 1 legal cardinal move (no diagonal or teleport jumps).

    Returns:
        Tuple[bool, str]: (is_valid, reason_message)
    """
    if path is None:
        return False, "Path is None."
    if not isinstance(path, list) or len(path) == 0:
        return False, "Path is empty."

    rows, cols = grid.shape

    # Check start and goal endpoints
    if path[0] != start:
        return False, f"Path begins at {path[0]}, but expected Start is {start}."
    if path[-1] != goal:
        return False, f"Path ends at {path[-1]}, but expected Goal is {goal}."

    # Edge case: Start equals Goal
    if len(path) == 1:
        r, c = path[0]
        if not (0 <= r < rows and 0 <= c < cols):
            return False, f"Start cell {path[0]} is out of bounds."
        if grid[r, c] == 1:
            return False, f"Start cell {path[0]} is on a wall."
        return True, "Valid single-cell path (Start == Goal)."

    # Validate all steps and transitions
    for i, cell in enumerate(path):
        r, c = cell
        if not (0 <= r < rows and 0 <= c < cols):
            return False, f"Step {i} ({cell}) is out of grid boundaries."
        if grid[r, c] == 1:
            return False, f"Step {i} ({cell}) lies on a wall."

        if i > 0:
            prev_r, prev_c = path[i - 1]
            dr = abs(r - prev_r)
            dc = abs(c - prev_c)
            # Manhattan distance must be exactly 1 for orthogonal movement
            if dr + dc != 1:
                return False, f"Invalid jump between step {i-1} ({path[i-1]}) and step {i} ({cell}). Distance: {dr+dc}."

    return True, "Path is valid and conforms to all rules."


def reconstruct_path(
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
) -> List[Tuple[int, int]]:
    """
    Reconstruct the path from start to goal by backtracking through parent pointers.
    Returns: List of coordinates from Start to Goal inclusive.
    """
    if start == goal:
        return [start]

    path: List[Tuple[int, int]] = []
    curr: Optional[Tuple[int, int]] = goal

    while curr is not None:
        path.append(curr)
        if curr == start:
            break
        curr = parent.get(curr)

    path.reverse()
    if path and path[0] == start:
        return path
    return []


# =============================================================================
# Experiment 4: Depth First Search (DFS) Implementation
# =============================================================================

def dfs(
    maze: Maze,
    start: Optional[Tuple[int, int]] = None,
    goal: Optional[Tuple[int, int]] = None,
) -> SearchResult:
    """
    Execute Depth First Search (DFS) using an explicit LIFO stack.

    Characteristics:
        - Frontier: Explicit stack (LIFO).
        - Exploration Strategy: Deepest unvisited node first.
        - Completeness: Complete in finite state spaces with cycle detection.
        - Optimality: Non-optimal (does not guarantee shortest path).
        - Neighbor Order: Deterministic (Up, Right, Down, Left).
        - Nodes Explored: Incremented upon popping a node from the stack.
    """
    # Defensive copy / coordinate defaults to prevent modifying original maze
    s = start if start is not None else maze.start
    g = goal if goal is not None else maze.goal

    # Validate coordinates
    if not (maze.is_in_bounds(s[0], s[1]) and maze.is_in_bounds(g[0], g[1])):
        return SearchResult(
            algorithm="DFS",
            path_found=False,
            path=None,
            nodes_explored=0,
            path_length=None,
            execution_time_ms=0.0,
            exploration_order=[],
            status_message="Start or Goal coordinate is out of bounds.",
        )

    if maze.is_wall(s[0], s[1]) or maze.is_wall(g[0], g[1]):
        return SearchResult(
            algorithm="DFS",
            path_found=False,
            path=None,
            nodes_explored=0,
            path_length=None,
            execution_time_ms=0.0,
            exploration_order=[],
            status_message="Start or Goal coordinate is placed inside a wall.",
        )

    # Begin high-precision timer (Experiment 10 / Experiment 4)
    t_start = time.perf_counter()

    # Stack holds tuples of (current_cell, parent_cell)
    stack: List[Tuple[Tuple[int, int], Optional[Tuple[int, int]]]] = [(s, None)]
    visited: Set[Tuple[int, int]] = set()
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}
    exploration_order: List[Tuple[int, int]] = []
    goal_found = False

    while stack:
        curr, prev = stack.pop()

        if curr in visited:
            continue

        visited.add(curr)
        parent[curr] = prev
        exploration_order.append(curr)

        # Goal test
        if curr == g:
            goal_found = True
            break

        # Push successors in reverse deterministic order so that
        # LEGAL_ACTIONS order (Up, Right, Down, Left) is popped first
        successors = maze.get_successors(curr)
        for next_state in reversed(successors):
            if next_state not in visited:
                stack.append((next_state, curr))

    t_end = time.perf_counter()
    execution_time_ms = (t_end - t_start) * 1000.0
    nodes_explored = len(exploration_order)

    if goal_found:
        raw_path = reconstruct_path(parent, s, g)
        is_valid, reason = validate_path(maze.grid, raw_path, s, g)
        if not is_valid:
            return SearchResult(
                algorithm="DFS",
                path_found=False,
                path=None,
                nodes_explored=nodes_explored,
                path_length=None,
                execution_time_ms=execution_time_ms,
                exploration_order=exploration_order,
                status_message=f"Path validation failed: {reason}",
            )

        path_length = len(raw_path) - 1
        return SearchResult(
            algorithm="DFS",
            path_found=True,
            path=raw_path,
            nodes_explored=nodes_explored,
            path_length=path_length,
            execution_time_ms=execution_time_ms,
            exploration_order=exploration_order,
            status_message=f"Success: Path of {path_length} steps found. Explored {nodes_explored} nodes.",
        )
    else:
        return SearchResult(
            algorithm="DFS",
            path_found=False,
            path=None,
            nodes_explored=nodes_explored,
            path_length=None,
            execution_time_ms=execution_time_ms,
            exploration_order=exploration_order,
            status_message=f"Failure: No route exists between {s} and {g}. Explored {nodes_explored} nodes.",
        )


# =============================================================================
# Experiment 5: Breadth First Search (BFS) Implementation
# =============================================================================

def bfs(
    maze: Maze,
    start: Optional[Tuple[int, int]] = None,
    goal: Optional[Tuple[int, int]] = None,
) -> SearchResult:
    """
    Execute Breadth First Search (BFS) using collections.deque (FIFO queue).

    Characteristics:
        - Frontier: FIFO queue.
        - Exploration Strategy: Level-by-level (shallowest nodes first).
        - Completeness: Complete in finite state spaces.
        - Optimality: Guaranteed optimal (shortest path) on unweighted grids.
        - Neighbor Order: Deterministic (Up, Right, Down, Left).
        - Visited Set: Nodes marked discovered when enqueued to eliminate duplicate entries.
        - Nodes Explored: Incremented upon popping a node from the queue.
    """
    s = start if start is not None else maze.start
    g = goal if goal is not None else maze.goal

    # Validate coordinates
    if not (maze.is_in_bounds(s[0], s[1]) and maze.is_in_bounds(g[0], g[1])):
        return SearchResult(
            algorithm="BFS",
            path_found=False,
            path=None,
            nodes_explored=0,
            path_length=None,
            execution_time_ms=0.0,
            exploration_order=[],
            status_message="Start or Goal coordinate is out of bounds.",
        )

    if maze.is_wall(s[0], s[1]) or maze.is_wall(g[0], g[1]):
        return SearchResult(
            algorithm="BFS",
            path_found=False,
            path=None,
            nodes_explored=0,
            path_length=None,
            execution_time_ms=0.0,
            exploration_order=[],
            status_message="Start or Goal coordinate is placed inside a wall.",
        )

    # Begin high-precision timer (Experiment 10 / Experiment 5)
    t_start = time.perf_counter()

    # FIFO queue with collections.deque
    queue: deque = deque([s])
    # Mark discovered upon enqueueing to prevent duplicate frontier entries
    discovered: Set[Tuple[int, int]] = {s}
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {s: None}
    exploration_order: List[Tuple[int, int]] = []
    goal_found = False

    while queue:
        curr = queue.popleft()
        exploration_order.append(curr)

        # Goal test
        if curr == g:
            goal_found = True
            break

        # Expand neighbors level-by-level in deterministic order
        for next_state in maze.get_successors(curr):
            if next_state not in discovered:
                discovered.add(next_state)
                parent[next_state] = curr
                queue.append(next_state)

    t_end = time.perf_counter()
    execution_time_ms = (t_end - t_start) * 1000.0
    nodes_explored = len(exploration_order)

    if goal_found:
        raw_path = reconstruct_path(parent, s, g)
        is_valid, reason = validate_path(maze.grid, raw_path, s, g)
        if not is_valid:
            return SearchResult(
                algorithm="BFS",
                path_found=False,
                path=None,
                nodes_explored=nodes_explored,
                path_length=None,
                execution_time_ms=execution_time_ms,
                exploration_order=exploration_order,
                status_message=f"Path validation failed: {reason}",
            )

        path_length = len(raw_path) - 1
        return SearchResult(
            algorithm="BFS",
            path_found=True,
            path=raw_path,
            nodes_explored=nodes_explored,
            path_length=path_length,
            execution_time_ms=execution_time_ms,
            exploration_order=exploration_order,
            status_message=f"Success: Optimal path of {path_length} steps found. Explored {nodes_explored} nodes.",
        )
    else:
        return SearchResult(
            algorithm="BFS",
            path_found=False,
            path=None,
            nodes_explored=nodes_explored,
            path_length=None,
            execution_time_ms=execution_time_ms,
            exploration_order=exploration_order,
            status_message=f"Failure: No route exists between {s} and {g}. Explored {nodes_explored} nodes.",
        )


# =============================================================================
# A* Search (Informed Search with Manhattan Heuristic)
# =============================================================================

def astar(
    maze: Maze,
    start: Optional[Tuple[int, int]] = None,
    goal: Optional[Tuple[int, int]] = None,
) -> SearchResult:
    """
    Execute A* Search using a Priority Queue (min-heap) and Manhattan Distance heuristic.

    Evaluation function:
        f(n) = g(n) + h(n)
        where:
            g(n) = exact path cost from start to node n
            h(n) = Manhattan distance from node n to goal (|r - g_r| + |c - g_c|)

    Characteristics:
        - Frontier: Min-heap priority queue.
        - Heuristic: Admissible and consistent (guarantees optimal shortest path).
        - Directivity: Strongly directed toward goal, exploring significantly fewer nodes than BFS.
    """
    s = start if start is not None else maze.start
    g = goal if goal is not None else maze.goal

    # Validate coordinates
    if not (maze.is_in_bounds(s[0], s[1]) and maze.is_in_bounds(g[0], g[1])):
        return SearchResult(
            algorithm="A*",
            path_found=False,
            path=None,
            nodes_explored=0,
            path_length=None,
            execution_time_ms=0.0,
            exploration_order=[],
            status_message="Start or Goal coordinate is out of bounds.",
        )

    if maze.is_wall(s[0], s[1]) or maze.is_wall(g[0], g[1]):
        return SearchResult(
            algorithm="A*",
            path_found=False,
            path=None,
            nodes_explored=0,
            path_length=None,
            execution_time_ms=0.0,
            exploration_order=[],
            status_message="Start or Goal coordinate is placed inside a wall.",
        )

    def manhattan(cell: Tuple[int, int]) -> int:
        return abs(cell[0] - g[0]) + abs(cell[1] - g[1])

    t_start = time.perf_counter()

    # Priority queue item: (f_score, h_score, tie_breaker, cell)
    tie_counter = 0
    start_h = manhattan(s)
    open_heap: List[Tuple[int, int, int, Tuple[int, int]]] = [(start_h, start_h, tie_counter, s)]
    
    g_score: Dict[Tuple[int, int], int] = {s: 0}
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {s: None}
    visited: Set[Tuple[int, int]] = set()
    exploration_order: List[Tuple[int, int]] = []
    goal_found = False

    while open_heap:
        f, h, _, curr = heapq.heappop(open_heap)

        if curr in visited:
            continue

        visited.add(curr)
        exploration_order.append(curr)

        # Goal test
        if curr == g:
            goal_found = True
            break

        current_g = g_score[curr]

        for next_state in maze.get_successors(curr):
            tentative_g = current_g + 1
            if next_state not in g_score or tentative_g < g_score[next_state]:
                g_score[next_state] = tentative_g
                parent[next_state] = curr
                h_val = manhattan(next_state)
                f_val = tentative_g + h_val
                tie_counter += 1
                heapq.heappush(open_heap, (f_val, h_val, tie_counter, next_state))

    t_end = time.perf_counter()
    execution_time_ms = (t_end - t_start) * 1000.0
    nodes_explored = len(exploration_order)

    if goal_found:
        raw_path = reconstruct_path(parent, s, g)
        is_valid, reason = validate_path(maze.grid, raw_path, s, g)
        if not is_valid:
            return SearchResult(
                algorithm="A*",
                path_found=False,
                path=None,
                nodes_explored=nodes_explored,
                path_length=None,
                execution_time_ms=execution_time_ms,
                exploration_order=exploration_order,
                status_message=f"Path validation failed: {reason}",
            )

        path_length = len(raw_path) - 1
        return SearchResult(
            algorithm="A*",
            path_found=True,
            path=raw_path,
            nodes_explored=nodes_explored,
            path_length=path_length,
            execution_time_ms=execution_time_ms,
            exploration_order=exploration_order,
            status_message=f"Success: Optimal path of {path_length} steps found with A*. Explored {nodes_explored} nodes.",
        )
    else:
        return SearchResult(
            algorithm="A*",
            path_found=False,
            path=None,
            nodes_explored=nodes_explored,
            path_length=None,
            execution_time_ms=execution_time_ms,
            exploration_order=exploration_order,
            status_message=f"Failure: No route exists between {s} and {g}. Explored {nodes_explored} nodes.",
        )


def compare_algorithms(maze: Maze) -> Tuple[SearchResult, SearchResult, str]:
    """
    Run DFS and BFS independently on an unchanged copy of the maze.
    Calculates empirical comparison metrics and generates an analytical summary.

    Returns:
        Tuple[SearchResult, SearchResult, str]: (dfs_result, bfs_result, comparison_summary)
    """
    # Clone maze to guarantee search operations cannot mutate the environment
    maze_copy_dfs = maze.clone()
    maze_copy_bfs = maze.clone()

    res_dfs = dfs(maze_copy_dfs)
    res_bfs = bfs(maze_copy_bfs)

    summary_lines = []
    summary_lines.append(f"Maze Size: {maze.rows}x{maze.cols} | Obstacle Density: {maze.wall_density():.1f}%")

    # 1. Path Found Comparison
    if res_dfs.path_found and res_bfs.path_found:
        summary_lines.append("Route Status: Both algorithms successfully found a route.")
    elif not res_dfs.path_found and not res_bfs.path_found:
        summary_lines.append("Route Status: Goal is unreachable. Neither algorithm found a route.")
    elif res_bfs.path_found and not res_dfs.path_found:
        summary_lines.append("Route Status: BFS reached the goal, but DFS failed.")
    else:
        summary_lines.append("Route Status: DFS reached the goal, but BFS failed.")

    # 2. Path Length Comparison
    if res_dfs.path_found and res_bfs.path_found:
        if res_bfs.path_length < res_dfs.path_length:
            diff = res_dfs.path_length - res_bfs.path_length
            summary_lines.append(f"Path Length: BFS found a shorter path ({res_bfs.path_length} steps vs DFS {res_dfs.path_length} steps, {diff} fewer steps).")
        elif res_bfs.path_length == res_dfs.path_length:
            summary_lines.append(f"Path Length: Equal ({res_bfs.path_length} steps each).")
        else:
            summary_lines.append(f"Path Length: DFS {res_dfs.path_length} steps, BFS {res_bfs.path_length} steps.")
    else:
        summary_lines.append("Path Length: Comparison unavailable because one or both algorithms found no route.")

    # 3. Nodes Explored Comparison
    if res_dfs.nodes_explored < res_bfs.nodes_explored:
        diff = res_bfs.nodes_explored - res_dfs.nodes_explored
        summary_lines.append(f"Exploration: DFS explored fewer nodes ({res_dfs.nodes_explored} vs BFS {res_bfs.nodes_explored}, diff: {diff}).")
    elif res_bfs.nodes_explored < res_dfs.nodes_explored:
        diff = res_dfs.nodes_explored - res_bfs.nodes_explored
        summary_lines.append(f"Exploration: BFS explored fewer nodes ({res_bfs.nodes_explored} vs DFS {res_dfs.nodes_explored}, diff: {diff}).")
    else:
        summary_lines.append(f"Exploration: Both explored exactly {res_bfs.nodes_explored} nodes.")

    # 4. Execution Time Comparison
    if res_dfs.execution_time_ms < res_bfs.execution_time_ms:
        summary_lines.append(f"Runtime: DFS was faster ({res_dfs.execution_time_ms:.3f} ms vs BFS {res_bfs.execution_time_ms:.3f} ms).")
    elif res_bfs.execution_time_ms < res_dfs.execution_time_ms:
        summary_lines.append(f"Runtime: BFS was faster ({res_bfs.execution_time_ms:.3f} ms vs DFS {res_dfs.execution_time_ms:.3f} ms).")
    else:
        summary_lines.append(f"Runtime: Measured execution times were identical ({res_dfs.execution_time_ms:.3f} ms).")

    summary_text = "\n".join(summary_lines)
    return res_dfs, res_bfs, summary_text
