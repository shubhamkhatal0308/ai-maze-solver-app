"""
visualization.py - Tkinter Canvas Rendering and Animation Engine
=================================================================
Artificial Intelligence Mini Project: AI Maze Solver & Route Visualizer
Experiments 1, 4, 5: Visual Representation & Non-blocking Search Animation

This module implements the grid renderer and non-blocking animation engine
using Tkinter Canvas and the .after() event loop scheduling mechanism.

Color Specifications:
    - Background:     #111827 (Dark Charcoal)
    - Empty cell:     #F3F4F6 (Light Gray / White)
    - Wall / Obstacle: #374151 (Dark Slate)
    - Start cell:     #22C55E (Vibrant Green)
    - Goal cell:      #EF4444 (Vibrant Red)
    - Explored cell:  #60A5FA (Soft Blue)
    - Final path:     #FACC15 (Vibrant Gold / Yellow)
    - Frontier:       #C084FC (Lavender Purple)
    - Grid lines:     #D1D5DB (Light Border)
"""

import tkinter as tk
from typing import Callable, List, Optional, Set, Tuple

from algorithms import SearchResult
from maze import Maze


# Palette definitions
COLOR_BG = "#111827"
COLOR_EMPTY = "#F3F4F6"
COLOR_WALL = "#374151"
COLOR_START = "#22C55E"
COLOR_GOAL = "#EF4444"
COLOR_EXPLORED = "#60A5FA"
COLOR_PATH = "#FACC15"
COLOR_FRONTIER = "#C084FC"
COLOR_GRID = "#9CA3AF"
COLOR_TEXT_LIGHT = "#FFFFFF"
COLOR_TEXT_DARK = "#111827"


class MazeCanvasView:
    """
    Renders the maze grid on a Tkinter Canvas and handles user click/drag
    interactions and step-by-step non-blocking search animations.
    """

    def __init__(
        self,
        parent: tk.Widget,
        maze: Maze,
        on_maze_modified: Optional[Callable[[], None]] = None,
        width: int = 560,
        height: int = 560,
    ):
        self.parent = parent
        self.maze = maze
        self.on_maze_modified = on_maze_modified

        self.canvas_width = width
        self.canvas_height = height
        self.cell_size: float = 24.0
        self.offset_x: float = 10.0
        self.offset_y: float = 10.0

        # State tracking
        self.explored_cells: Set[Tuple[int, int]] = set()
        self.path_cells: Set[Tuple[int, int]] = set()
        self.path_sequence: List[Tuple[int, int]] = []
        self.frontier_cells: Set[Tuple[int, int]] = set()

        # Animation state
        self.is_animating: bool = False
        self._after_id: Optional[str] = None
        self._on_animation_complete: Optional[Callable[[], None]] = None

        # Interaction mode: 'wall', 'start', 'goal'
        self.interaction_mode: str = "wall"
        self._is_dragging: bool = False
        self._drag_target_val: Optional[int] = None

        # Initialize Canvas
        self.canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=COLOR_BG,
            highlightthickness=1,
            highlightbackground="#374151",
            relief="flat",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Button-3>", self._on_right_click)  # Right click quick toggle

        self.recalculate_geometry()
        self.redraw()

    def set_maze(self, new_maze: Maze) -> None:
        """Replace the current maze model and refresh the display."""
        self.stop_animation()
        self.maze = new_maze
        self.reset_visualization_state()
        self.recalculate_geometry()
        self.redraw()

    def set_interaction_mode(self, mode: str) -> None:
        """Set mouse click behavior: 'wall', 'start', or 'goal'."""
        self.interaction_mode = mode

    def recalculate_geometry(self) -> None:
        """Compute optimal cell sizes and offsets to center the maze neatly."""
        w = max(self.canvas.winfo_width(), self.canvas_width)
        h = max(self.canvas.winfo_height(), self.canvas_height)

        padding = 16.0
        available_w = max(100.0, w - (padding * 2))
        available_h = max(100.0, h - (padding * 2))

        cell_w = available_w / max(1, self.maze.cols)
        cell_h = available_h / max(1, self.maze.rows)
        self.cell_size = max(8.0, min(cell_w, cell_h))

        grid_w = self.cell_size * self.maze.cols
        grid_h = self.cell_size * self.maze.rows
        self.offset_x = (w - grid_w) / 2.0
        self.offset_y = (h - grid_h) / 2.0

    def _on_resize(self, event) -> None:
        """Handle canvas resize to keep the grid sharp and well-proportioned."""
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.recalculate_geometry()
        self.redraw()

    def get_cell_from_pixel(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        """Translate canvas pixel coordinates into grid (row, col) coordinates."""
        col = int((x - self.offset_x) // self.cell_size)
        row = int((y - self.offset_y) // self.cell_size)
        if 0 <= row < self.maze.rows and 0 <= col < self.maze.cols:
            return (row, col)
        return None

    def _on_mouse_down(self, event) -> None:
        if self.is_animating:
            return
        cell = self.get_cell_from_pixel(event.x, event.y)
        if not cell:
            return

        r, c = cell
        if self.interaction_mode == "start":
            if self.maze.set_start(r, c):
                self.reset_visualization_state()
                self.redraw()
                if self.on_maze_modified:
                    self.on_maze_modified()
        elif self.interaction_mode == "goal":
            if self.maze.set_goal(r, c):
                self.reset_visualization_state()
                self.redraw()
                if self.on_maze_modified:
                    self.on_maze_modified()
        else:
            # Wall toggle/draw mode
            if cell != self.maze.start and cell != self.maze.goal:
                current_val = self.maze.grid[r, c]
                self._drag_target_val = 0 if current_val == 1 else 1
                self.maze.grid[r, c] = self._drag_target_val
                self.reset_visualization_state()
                self.draw_cell(r, c)
                if self.on_maze_modified:
                    self.on_maze_modified()
            self._is_dragging = True

    def _on_mouse_drag(self, event) -> None:
        if self.is_animating or not self._is_dragging or self._drag_target_val is None:
            return
        cell = self.get_cell_from_pixel(event.x, event.y)
        if not cell:
            return
        r, c = cell
        if cell != self.maze.start and cell != self.maze.goal:
            if self.maze.grid[r, c] != self._drag_target_val:
                self.maze.grid[r, c] = self._drag_target_val
                self.reset_visualization_state()
                self.draw_cell(r, c)
                if self.on_maze_modified:
                    self.on_maze_modified()

    def _on_mouse_up(self, event) -> None:
        self._is_dragging = False
        self._drag_target_val = None

    def _on_right_click(self, event) -> None:
        """Right click quick-toggles walls regardless of selected mode."""
        if self.is_animating:
            return
        cell = self.get_cell_from_pixel(event.x, event.y)
        if cell and cell != self.maze.start and cell != self.maze.goal:
            self.maze.toggle_wall(cell[0], cell[1])
            self.reset_visualization_state()
            self.draw_cell(cell[0], cell[1])
            if self.on_maze_modified:
                self.on_maze_modified()

    # =========================================================================
    # Rendering Methods
    # =========================================================================

    def reset_visualization_state(self) -> None:
        """Clear search trails (explored cells and path) while keeping walls."""
        self.explored_cells.clear()
        self.path_cells.clear()
        self.path_sequence.clear()
        self.frontier_cells.clear()

    def get_cell_color(self, r: int, c: int) -> str:
        """Determine display color of a cell based on priority rules."""
        coord = (r, c)
        if coord == self.maze.start:
            return COLOR_START
        if coord == self.maze.goal:
            return COLOR_GOAL
        if coord in self.path_cells:
            return COLOR_PATH
        if coord in self.frontier_cells:
            return COLOR_FRONTIER
        if coord in self.explored_cells:
            return COLOR_EXPLORED
        if self.maze.grid[r, c] == 1:
            return COLOR_WALL
        return COLOR_EMPTY

    def draw_cell(self, r: int, c: int) -> None:
        """
        Incrementally redraw a single cell on the canvas.
        Fast O(1) rendering for animation steps.
        """
        tag = f"cell_{r}_{c}"
        self.canvas.delete(tag)

        x1 = self.offset_x + (c * self.cell_size)
        y1 = self.offset_y + (r * self.cell_size)
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size

        color = self.get_cell_color(r, c)
        # Border outline: subtle for empty, darker for walls
        outline_color = "#374151" if self.maze.grid[r, c] == 1 else "#D1D5DB"

        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            outline=outline_color,
            width=1,
            tags=(tag, "cell"),
        )

        # Draw markers on Start and Goal
        coord = (r, c)
        if coord == self.maze.start or coord == self.maze.goal:
            font_size = max(8, int(self.cell_size * 0.45))
            text = "S" if coord == self.maze.start else "G"
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            self.canvas.create_text(
                cx, cy,
                text=text,
                fill=COLOR_TEXT_LIGHT,
                font=("Arial", font_size, "bold"),
                tags=(tag, "marker"),
            )

    def redraw(self) -> None:
        """Full repaint of the maze grid."""
        self.canvas.delete("all")
        for r in range(self.maze.rows):
            for c in range(self.maze.cols):
                self.draw_cell(r, c)

    def display_static_result(self, result: SearchResult) -> None:
        """Instantly show search exploration and final path without animation."""
        self.stop_animation()
        self.reset_visualization_state()
        self.explored_cells = set(result.exploration_order)
        if result.path_found and result.path:
            self.path_cells = set(result.path)
            self.path_sequence = list(result.path)
        self.redraw()

    # =========================================================================
    # Non-blocking Animation Engine (Tkinter .after)
    # =========================================================================

    def animate_search(
        self,
        result: SearchResult,
        speed_ms: int = 20,
        on_step: Optional[Callable[[int, int], None]] = None,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Execute non-blocking animation of the search algorithm.
        Phase 1: Explores cells in order of expansion.
        Phase 2: Traces the final reconstructed path in vibrant yellow.
        """
        self.stop_animation()
        self.reset_visualization_state()
        self.redraw()

        self.is_animating = True
        self._on_animation_complete = on_complete

        # Handle instant speed (0 ms)
        if speed_ms <= 0:
            self.display_static_result(result)
            self.is_animating = False
            if on_complete:
                on_complete()
            return

        order = result.exploration_order
        path = result.path if (result.path_found and result.path) else []
        total_explored = len(order)

        def step_explore(idx: int) -> None:
            if not self.is_animating:
                return

            # Batch multiple cells per frame if speed is very fast
            batch_size = 1 if speed_ms >= 15 else 4

            for _ in range(batch_size):
                if idx >= total_explored:
                    break
                cell = order[idx]
                self.explored_cells.add(cell)
                self.draw_cell(cell[0], cell[1])
                if on_step:
                    on_step(idx + 1, total_explored)
                idx += 1

            if idx < total_explored:
                self._after_id = self.canvas.after(speed_ms, lambda: step_explore(idx))
            else:
                # Phase 2: Trace final path
                if path:
                    self._after_id = self.canvas.after(max(40, speed_ms * 2), lambda: step_path(0))
                else:
                    self._finish_animation()

        def step_path(path_idx: int) -> None:
            if not self.is_animating:
                return

            if path_idx < len(path):
                cell = path[path_idx]
                self.path_cells.add(cell)
                self.draw_cell(cell[0], cell[1])
                # Double delay for path highlight to make it dramatic and clear
                self._after_id = self.canvas.after(max(25, speed_ms), lambda: step_path(path_idx + 1))
            else:
                self._finish_animation()

        # Kick off Phase 1
        self._after_id = self.canvas.after(speed_ms, lambda: step_explore(0))

    def _finish_animation(self) -> None:
        """Clean up when animation completes normally."""
        self.is_animating = False
        self._after_id = None
        if self._on_animation_complete:
            cb = self._on_animation_complete
            self._on_animation_complete = None
            cb()

    def stop_animation(self) -> None:
        """
        Safely halt any active animation immediately.
        Restores state without corrupting the maze model.
        """
        if self._after_id is not None:
            try:
                self.canvas.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

        if self.is_animating:
            self.is_animating = False
            if self._on_animation_complete:
                cb = self._on_animation_complete
                self._on_animation_complete = None
                cb()
