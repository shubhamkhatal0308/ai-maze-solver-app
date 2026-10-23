"""
main.py - Application Entry Point and GUI Integration
======================================================
Artificial Intelligence Mini Project: AI Maze Solver & Route Visualizer
College Level Demonstration Platform

Features:
    - Tkinter & ttk Dark Theme Desktop GUI.
    - Interactive Canvas for State Space exploration and mouse-driven wall editing.
    - Step-by-step non-blocking animation for DFS and BFS.
    - Embedded Matplotlib comparison charts using FigureCanvasTkAgg.
    - Empirical performance comparison (Nodes Explored, Path Length, Execution Time).
    - Preset demonstration mazes and random solvable maze generator.
"""

import os
import sys
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple

# Matplotlib backend setup before canvas import
if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "ai_maze_solver_mpl")

import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from maze import Maze
from algorithms import dfs, bfs, astar, compare_algorithms, SearchResult
from visualization import (
    MazeCanvasView,
    COLOR_BG,
    COLOR_EMPTY,
    COLOR_WALL,
    COLOR_START,
    COLOR_GOAL,
    COLOR_EXPLORED,
    COLOR_PATH,
    COLOR_FRONTIER,
)
from charts import create_comparison_figure, render_comparison_charts


# Theme Styling Colors
PANEL_BG = "#1F2937"       # Charcoal panel
CARD_BG = "#111827"        # Dark slate
BORDER_COLOR = "#374151"   # Boundary outline
TEXT_PRIMARY = "#F9FAFB"   # White text
TEXT_SECONDARY = "#9CA3AF" # Muted text
ACCENT_BLUE = "#3B82F6"
ACCENT_GREEN = "#10B981"
ACCENT_RED = "#EF4444"
ACCENT_YELLOW = "#F59E0B"
ACCENT_PURPLE = "#8B5CF6"


class AIMazeSolverApp(tk.Tk):
    """
    Main Application Window for AI Maze Solver & Route Visualizer.
    """

    def __init__(self):
        super().__init__()

        self.title("AI Maze Solver & Route Visualizer")
        self.geometry("1280x820")
        self.minsize(1050, 700)
        self.configure(bg=COLOR_BG)

        # Application state
        self.current_rows: int = 15
        self.current_cols: int = 15
        self.maze: Maze = Maze.create_preset("demo_15x15")

        self.latest_dfs_result: Optional[SearchResult] = None
        self.latest_bfs_result: Optional[SearchResult] = None

        # Speed mapping (ms delay per exploration frame)
        self.speed_map = {
            "Slow (50ms)": 50,
            "Normal (20ms)": 20,
            "Fast (5ms)": 5,
            "Instant (0ms)": 0,
        }

        # Setup ttk styles for dark modern look
        self._setup_styles()

        # Build UI layout
        self._build_header()
        self._build_main_layout()

        # Handle window closing cleanly
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Initial render of charts in empty state
        self.update_charts_display()

    # =========================================================================
    # UI Styling
    # =========================================================================

    def _setup_styles(self) -> None:
        """Configure ttk widgets with dark theme properties."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=COLOR_BG)
        style.configure("Panel.TFrame", background=PANEL_BG)
        style.configure("Card.TFrame", background=CARD_BG, relief="flat")

        style.configure(
            "TLabel",
            background=PANEL_BG,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
        )
        style.configure(
            "HeaderTitle.TLabel",
            background=COLOR_BG,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "HeaderSub.TLabel",
            background=COLOR_BG,
            foreground=TEXT_SECONDARY,
            font=("Segoe UI", 10),
        )
        style.configure(
            "CardTitle.TLabel",
            background=CARD_BG,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "CardText.TLabel",
            background=CARD_BG,
            foreground=TEXT_SECONDARY,
            font=("Segoe UI", 9),
        )
        style.configure(
            "CardValue.TLabel",
            background=CARD_BG,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
        )

        style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL_BG, foreground=TEXT_PRIMARY, padding=[12, 6], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", ACCENT_BLUE)], foreground=[("selected", "#FFFFFF")])

        style.configure("TCombobox", fieldbackground="#374151", background="#4B5563", foreground="#FFFFFF")
        style.configure("TCheckbutton", background=PANEL_BG, foreground=TEXT_PRIMARY, font=("Segoe UI", 9))
        style.configure("TRadiobutton", background=PANEL_BG, foreground=TEXT_PRIMARY, font=("Segoe UI", 9))

    # =========================================================================
    # Header Section
    # =========================================================================

    def _build_header(self) -> None:
        """Create the top banner with title, subtitle, and dynamic status badge."""
        header_frame = tk.Frame(self, bg=COLOR_BG, padx=20, pady=12)
        header_frame.pack(fill=tk.X)

        text_container = tk.Frame(header_frame, bg=COLOR_BG)
        text_container.pack(side=tk.LEFT)

        title_lbl = ttk.Label(text_container, text="AI Maze Solver & Route Visualizer", style="HeaderTitle.TLabel")
        title_lbl.pack(anchor="w")

        sub_lbl = ttk.Label(
            text_container,
            text="Explore, Solve, and Compare State Space Search Algorithms (DFS vs BFS)",
            style="HeaderSub.TLabel",
        )
        sub_lbl.pack(anchor="w")

        # Right side status badge
        status_box = tk.Frame(header_frame, bg=PANEL_BG, padx=12, pady=6, highlightbackground=BORDER_COLOR, highlightthickness=1)
        status_box.pack(side=tk.RIGHT)

        tk.Label(status_box, text="STATUS:", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.status_badge = tk.Label(status_box, text="READY", bg="#065F46", fg="#34D399", font=("Segoe UI", 9, "bold"), padx=8, pady=2)
        self.status_badge.pack(side=tk.LEFT)

    # =========================================================================
    # Main Layout
    # =========================================================================

    def _build_main_layout(self) -> None:
        """Construct the split layout: Left Control/Summary Panel, Right Display Area."""
        main_container = tk.Frame(self, bg=COLOR_BG, padx=16, pady=8)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left Column: Control Panel & Result Cards
        left_column = tk.Frame(main_container, bg=PANEL_BG, width=380, padx=14, pady=14, highlightbackground=BORDER_COLOR, highlightthickness=1)
        left_column.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))
        left_column.pack_propagate(False)

        # Make left column scrollable to ensure usability on smaller screens
        self._build_control_panel(left_column)

        # Right Column: Notebook with Visualizer Canvas & Matplotlib Charts
        right_column = tk.Frame(main_container, bg=COLOR_BG)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(right_column)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Maze Visualizer
        self.tab_visualizer = tk.Frame(self.notebook, bg=COLOR_BG)
        self.notebook.add(self.tab_visualizer, text="  Interactive Maze Visualizer  ")

        # Tab 2: Performance Analytics & Charts
        self.tab_analytics = tk.Frame(self.notebook, bg=COLOR_BG)
        self.notebook.add(self.tab_analytics, text="  Performance Comparison Charts  ")

        self._build_visualizer_tab(self.tab_visualizer)
        self._build_analytics_tab(self.tab_analytics)

    # =========================================================================
    # Control Panel (Left Column)
    # =========================================================================

    def _build_control_panel(self, parent: tk.Frame) -> None:
        """Populate the left panel with algorithm triggers, maze config, and result cards."""
        # Use a canvas + scrollbar inside left column for guaranteed responsive scrolling
        canvas = tk.Canvas(parent, bg=PANEL_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=PANEL_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)

        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)

        # Allow mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Section: Algorithm Controls
        sec_algo = self._create_section(scrollable_frame, "1. SEARCH ALGORITHMS")

        btn_row1 = tk.Frame(sec_algo, bg=PANEL_BG)
        btn_row1.pack(fill=tk.X, pady=3)
        self.btn_dfs = tk.Button(
            btn_row1, text="▶ Run DFS", bg="#BE185D", fg="#FFFFFF",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            command=self.run_dfs, padx=4, pady=5,
        )
        self.btn_dfs.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        self.btn_bfs = tk.Button(
            btn_row1, text="▶ Run BFS", bg="#1D4ED8", fg="#FFFFFF",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            command=self.run_bfs, padx=4, pady=5,
        )
        self.btn_bfs.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.btn_astar = tk.Button(
            btn_row1, text="▶ Run A*", bg="#7C3AED", fg="#FFFFFF",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            command=self.run_astar, padx=4, pady=5,
        )
        self.btn_astar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        self.btn_compare = tk.Button(
            sec_algo, text="⚡ Compare Algorithms (DFS vs BFS)", bg="#059669", fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            command=self.run_compare, pady=7,
        )
        self.btn_compare.pack(fill=tk.X, pady=(6, 3))

        # Stop Animation button
        self.btn_stop = tk.Button(
            sec_algo, text="⏹ Stop Animation", bg="#DC2626", fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"), relief="flat", state=tk.DISABLED,
            command=self.stop_current_animation, pady=4,
        )
        self.btn_stop.pack(fill=tk.X, pady=(2, 6))

        # Section: Maze Configuration
        sec_maze = self._create_section(scrollable_frame, "2. MAZE SETUP & PRESETS")

        # Maze Size Selector
        size_frame = tk.Frame(sec_maze, bg=PANEL_BG)
        size_frame.pack(fill=tk.X, pady=2)
        tk.Label(size_frame, text="Grid Size:", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.combo_size = ttk.Combobox(
            size_frame, values=["10x10", "15x15", "20x20"], state="readonly", width=10
        )
        self.combo_size.set("15x15")
        self.combo_size.pack(side=tk.RIGHT)
        self.combo_size.bind("<<ComboboxSelected>>", self._on_size_change)

        # Preset & Random Buttons
        btn_row2 = tk.Frame(sec_maze, bg=PANEL_BG)
        btn_row2.pack(fill=tk.X, pady=4)
        self.btn_random = tk.Button(
            btn_row2, text="Random Maze", bg="#374151", fg=TEXT_PRIMARY,
            font=("Segoe UI", 8, "bold"), relief="flat", command=self.generate_random_maze, pady=4
        )
        self.btn_random.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        self.btn_preset = tk.Button(
            btn_row2, text="Demo Preset", bg="#374151", fg=TEXT_PRIMARY,
            font=("Segoe UI", 8, "bold"), relief="flat", command=self.load_demo_preset, pady=4
        )
        self.btn_preset.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.btn_reset = tk.Button(
            btn_row2, text="Reset Search", bg="#374151", fg=TEXT_PRIMARY,
            font=("Segoe UI", 8, "bold"), relief="flat", command=self.reset_search, pady=4
        )
        self.btn_reset.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.btn_clear = tk.Button(
            btn_row2, text="Clear Walls", bg="#374151", fg=TEXT_PRIMARY,
            font=("Segoe UI", 8, "bold"), relief="flat", command=self.clear_all_walls, pady=4
        )
        self.btn_clear.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        # Section: Mouse Click Mode
        sec_mode = self._create_section(scrollable_frame, "3. MOUSE INTERACTION")
        self.interaction_var = tk.StringVar(value="wall")

        mode_row = tk.Frame(sec_mode, bg=PANEL_BG)
        mode_row.pack(fill=tk.X, pady=2)
        ttk.Radiobutton(mode_row, text="Wall Draw/Erase", variable=self.interaction_var, value="wall", command=self._on_mode_change).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Radiobutton(mode_row, text="Set Start", variable=self.interaction_var, value="start", command=self._on_mode_change).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(mode_row, text="Set Goal", variable=self.interaction_var, value="goal", command=self._on_mode_change).pack(side=tk.LEFT, padx=6)

        # Section: Animation Preferences
        sec_anim = self._create_section(scrollable_frame, "4. ANIMATION SETTINGS")

        anim_row = tk.Frame(sec_anim, bg=PANEL_BG)
        anim_row.pack(fill=tk.X, pady=2)

        self.show_anim_var = tk.BooleanVar(value=True)
        self.chk_anim = ttk.Checkbutton(anim_row, text="Animate Search", variable=self.show_anim_var)
        self.chk_anim.pack(side=tk.LEFT)

        self.combo_speed = ttk.Combobox(
            anim_row, values=list(self.speed_map.keys()), state="readonly", width=14
        )
        self.combo_speed.set("Normal (20ms)")
        self.combo_speed.pack(side=tk.RIGHT)

        # Section: Results Cards (DFS & BFS)
        sec_results = self._create_section(scrollable_frame, "5. SEARCH METRICS")
        self._build_result_cards(sec_results)

    def _create_section(self, parent: tk.Frame, title: str) -> tk.Frame:
        """Create a neatly boxed section inside the control panel."""
        frame = tk.Frame(parent, bg=PANEL_BG, pady=6)
        frame.pack(fill=tk.X, pady=4)
        lbl = tk.Label(frame, text=title, bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 8, "bold"))
        lbl.pack(anchor="w", pady=(0, 4))
        return frame

    # =========================================================================
    # Results Panel (DFS & BFS Cards)
    # =========================================================================

    def _build_result_cards(self, parent: tk.Frame) -> None:
        """Create dual result cards for DFS and BFS."""
        # DFS Card
        self.card_dfs = tk.Frame(parent, bg=CARD_BG, padx=10, pady=8, highlightbackground="#BE185D", highlightthickness=1)
        self.card_dfs.pack(fill=tk.X, pady=(2, 6))

        tk.Label(self.card_dfs, text="DEPTH FIRST SEARCH (DFS)", bg=CARD_BG, fg="#F472B6", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.lbl_dfs_path = tk.Label(self.card_dfs, text="Path Found: -", bg=CARD_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9))
        self.lbl_dfs_path.pack(anchor="w")
        self.lbl_dfs_nodes = tk.Label(self.card_dfs, text="Nodes Explored: -", bg=CARD_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9))
        self.lbl_dfs_nodes.pack(anchor="w")
        self.lbl_dfs_len = tk.Label(self.card_dfs, text="Path Length: -", bg=CARD_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9))
        self.lbl_dfs_len.pack(anchor="w")
        self.lbl_dfs_time = tk.Label(self.card_dfs, text="Execution Time: -", bg=CARD_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9))
        self.lbl_dfs_time.pack(anchor="w")

        # BFS Card
        self.card_bfs = tk.Frame(parent, bg=CARD_BG, padx=10, pady=8, highlightbackground="#1D4ED8", highlightthickness=1)
        self.card_bfs.pack(fill=tk.X, pady=(2, 6))

        tk.Label(self.card_bfs, text="BREADTH FIRST SEARCH (BFS)", bg=CARD_BG, fg="#60A5FA", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.lbl_bfs_path = tk.Label(self.card_bfs, text="Path Found: -", bg=CARD_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9))
        self.lbl_bfs_path.pack(anchor="w")
        self.lbl_bfs_nodes = tk.Label(self.card_bfs, text="Nodes Explored: -", bg=CARD_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9))
        self.lbl_bfs_nodes.pack(anchor="w")
        self.lbl_bfs_len = tk.Label(self.card_bfs, text="Path Length: -", bg=CARD_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9))
        self.lbl_bfs_len.pack(anchor="w")
        self.lbl_bfs_time = tk.Label(self.card_bfs, text="Execution Time: -", bg=CARD_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 9))
        self.lbl_bfs_time.pack(anchor="w")

        # Summary box
        self.summary_box = tk.Label(
            parent,
            text="Ready. Select an algorithm to solve or click 'Compare Algorithms'.",
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 8),
            justify=tk.LEFT,
            wraplength=340,
            padx=8,
            pady=6,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
        )
        self.summary_box.pack(fill=tk.X, pady=(2, 4))

    # =========================================================================
    # Visualizer Tab (Canvas & Color Legend)
    # =========================================================================

    def _build_visualizer_tab(self, parent: tk.Frame) -> None:
        """Construct the maze canvas view and legend bar."""
        canvas_container = tk.Frame(parent, bg=COLOR_BG)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))

        self.canvas_view = MazeCanvasView(
            canvas_container,
            self.maze,
            on_maze_modified=self._on_maze_user_modified,
            width=680,
            height=580,
        )

        # Legend Bar
        legend_frame = tk.Frame(parent, bg=PANEL_BG, padx=12, pady=6, highlightbackground=BORDER_COLOR, highlightthickness=1)
        legend_frame.pack(fill=tk.X, padx=8, pady=(4, 8))

        tk.Label(legend_frame, text="COLOR LEGEND:", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, padx=(0, 8))

        legend_items = [
            ("Start", COLOR_START),
            ("Goal", COLOR_GOAL),
            ("Wall", COLOR_WALL),
            ("Empty", COLOR_EMPTY),
            ("Explored", COLOR_EXPLORED),
            ("Final Path", COLOR_PATH),
        ]

        for name, col in legend_items:
            item_box = tk.Frame(legend_frame, bg=PANEL_BG)
            item_box.pack(side=tk.LEFT, padx=6)
            tk.Label(item_box, text="  ", bg=col, relief="solid", borderwidth=1).pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(item_box, text=name, bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 8)).pack(side=tk.LEFT)

    # =========================================================================
    # Analytics Tab (Embedded Matplotlib Charts)
    # =========================================================================

    def _build_analytics_tab(self, parent: tk.Frame) -> None:
        """Construct the Matplotlib comparison charts embedded into Tkinter."""
        chart_container = tk.Frame(parent, bg=COLOR_BG, padx=10, pady=10)
        chart_container.pack(fill=tk.BOTH, expand=True)

        self.fig = create_comparison_figure()
        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=chart_container)
        self.canvas_chart.draw()
        self.canvas_chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # In-depth comparison card below charts
        detail_frame = tk.Frame(parent, bg=PANEL_BG, padx=14, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        detail_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(detail_frame, text="ALGORITHM PERFORMANCE ANALYSIS", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.lbl_detail_analysis = tk.Label(
            detail_frame,
            text="No comparative search performed yet. Run 'Compare Algorithms' to plot empirical results.",
            bg=PANEL_BG,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9),
            justify=tk.LEFT,
        )
        self.lbl_detail_analysis.pack(anchor="w", pady=(4, 0))

    # =========================================================================
    # User Interactions & Event Handlers
    # =========================================================================

    def _on_mode_change(self) -> None:
        """Update canvas interaction mode from radio buttons."""
        mode = self.interaction_var.get()
        self.canvas_view.set_interaction_mode(mode)

    def _on_maze_user_modified(self) -> None:
        """Triggered when user clicks or draws on canvas."""
        self._set_status("READY", "#065F46", "#34D399")
        self.summary_box.config(text="Maze modified by user. Ready for search.")

    def _on_size_change(self, event) -> None:
        """Handle maze dimension selection."""
        val = self.combo_size.get()
        if val == "10x10":
            rows, cols = 10, 10
        elif val == "20x20":
            rows, cols = 20, 20
        else:
            rows, cols = 15, 15

        self.current_rows, self.current_cols = rows, cols
        new_maze = Maze(rows=rows, cols=cols, start=(0, 0), goal=(rows - 1, cols - 1))
        new_maze.generate_random(density=0.28, guarantee_solvable=True)
        self.maze = new_maze
        self.canvas_view.set_maze(new_maze)
        self.reset_results_display()
        self._set_status("READY", "#065F46", "#34D399")
        self.summary_box.config(text=f"Grid resized to {rows}x{cols}. Random solvable maze generated.")

    def _set_status(self, text: str, bg_color: str, fg_color: str) -> None:
        """Update the top right status badge."""
        self.status_badge.config(text=text, bg=bg_color, fg=fg_color)

    def _set_controls_enabled(self, enabled: bool) -> None:
        """Enable or disable interactive buttons during running search animation."""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.btn_dfs.config(state=state)
        self.btn_bfs.config(state=state)
        self.btn_astar.config(state=state)
        self.btn_compare.config(state=state)
        self.btn_random.config(state=state)
        self.btn_preset.config(state=state)
        self.btn_reset.config(state=state)
        self.btn_clear.config(state=state)
        self.combo_size.config(state="readonly" if enabled else tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED if enabled else tk.NORMAL)

    # =========================================================================
    # Action Triggers
    # =========================================================================

    def generate_random_maze(self) -> None:
        """Generate a fresh random solvable maze."""
        self.canvas_view.stop_animation()
        self.maze.generate_random(density=0.28, guarantee_solvable=True)
        self.canvas_view.set_maze(self.maze)
        self.reset_results_display()
        self._set_status("READY", "#065F46", "#34D399")
        self.summary_box.config(text=f"New random maze generated ({self.maze.wall_density():.1f}% walls).")

    def load_demo_preset(self) -> None:
        """Load the handcrafted preset demo maze showcasing DFS vs BFS differences."""
        self.canvas_view.stop_animation()
        if self.current_rows == 10:
            self.maze = Maze.create_preset("demo_10x10")
        elif self.current_rows == 20:
            self.maze = Maze.create_preset("demo_20x20")
        else:
            self.maze = Maze.create_preset("demo_15x15")

        self.canvas_view.set_maze(self.maze)
        self.reset_results_display()
        self._set_status("READY", "#065F46", "#34D399")
        self.summary_box.config(text="Loaded demonstration preset maze. Run Compare Algorithms to see DFS vs BFS!")

    def reset_search(self) -> None:
        """Clear search trails on canvas while preserving walls."""
        self.canvas_view.stop_animation()
        self.canvas_view.reset_visualization_state()
        self.canvas_view.redraw()
        self.reset_results_display()
        self._set_status("READY", "#065F46", "#34D399")
        self.summary_box.config(text="Search visualization and metrics reset. Ready for search.")

    def clear_all_walls(self) -> None:
        """Wipe all walls, creating a clean open grid."""
        self.canvas_view.stop_animation()
        self.maze.clear_walls()
        self.canvas_view.reset_visualization_state()
        self.canvas_view.redraw()
        self.reset_results_display()
        self._set_status("READY", "#065F46", "#34D399")
        self.summary_box.config(text="All walls removed. Open grid ready.")

    def stop_current_animation(self) -> None:
        """Safely halt running animation without corrupting maze."""
        self.canvas_view.stop_animation()
        self._set_controls_enabled(True)
        self._set_status("READY", "#065F46", "#34D399")
        self.summary_box.config(text="Animation stopped by user.")

    # =========================================================================
    # Algorithm Execution
    # =========================================================================

    def run_dfs(self) -> None:
        """Execute and visualize Depth First Search."""
        self._set_controls_enabled(False)
        self._set_status("SEARCHING", "#92400E", "#FCD34D")
        self.notebook.select(self.tab_visualizer)

        result = dfs(self.maze)
        self.latest_dfs_result = result
        self.update_dfs_card(result)

        speed_name = self.combo_speed.get()
        speed_ms = self.speed_map.get(speed_name, 20) if self.show_anim_var.get() else 0

        def on_complete():
            self._set_controls_enabled(True)
            if result.path_found:
                self._set_status("SOLVED", "#065F46", "#34D399")
                self.summary_box.config(text=f"DFS completed: Path of {result.path_length} steps found. Explored {result.nodes_explored} nodes.")
            else:
                self._set_status("NO PATH", "#991B1B", "#FCA5A5")
                self.summary_box.config(text="DFS completed: No path exists to the goal.")

        self.canvas_view.animate_search(result, speed_ms=speed_ms, on_complete=on_complete)

    def run_astar(self) -> None:
        """Execute and visualize A* Search with Manhattan heuristic."""
        self._set_controls_enabled(False)
        self._set_status("SEARCHING", "#5B21B6", "#DDD6FE")
        self.notebook.select(self.tab_visualizer)

        result = astar(self.maze)
        self.latest_bfs_result = result
        self.update_bfs_card(result)

        speed_name = self.combo_speed.get()
        speed_ms = self.speed_map.get(speed_name, 20) if self.show_anim_var.get() else 0

        def on_complete():
            self._set_controls_enabled(True)
            if result.path_found:
                self._set_status("SOLVED", "#065F46", "#34D399")
                self.summary_box.config(text=f"A* completed: Optimal path of {result.path_length} steps found. Explored {result.nodes_explored} nodes.")
            else:
                self._set_status("NO PATH", "#991B1B", "#FCA5A5")
                self.summary_box.config(text="A* completed: No path exists to the goal.")

        self.canvas_view.animate_search(result, speed_ms=speed_ms, on_complete=on_complete)


    def run_bfs(self) -> None:
        """Execute and visualize Breadth First Search."""
        self._set_controls_enabled(False)
        self._set_status("SEARCHING", "#1E40AF", "#93C5FD")
        self.notebook.select(self.tab_visualizer)

        result = bfs(self.maze)
        self.latest_bfs_result = result
        self.update_bfs_card(result)

        speed_name = self.combo_speed.get()
        speed_ms = self.speed_map.get(speed_name, 20) if self.show_anim_var.get() else 0

        def on_complete():
            self._set_controls_enabled(True)
            if result.path_found:
                self._set_status("SOLVED", "#065F46", "#34D399")
                self.summary_box.config(text=f"BFS completed: Optimal path of {result.path_length} steps found. Explored {result.nodes_explored} nodes.")
            else:
                self._set_status("NO PATH", "#991B1B", "#FCA5A5")
                self.summary_box.config(text="BFS completed: No path exists to the goal.")

        self.canvas_view.animate_search(result, speed_ms=speed_ms, on_complete=on_complete)


    def run_compare(self) -> None:
        """Run DFS and BFS independently, update cards, refresh charts, and show summary."""
        self.canvas_view.stop_animation()
        self._set_status("COMPARING", "#4C1D95", "#C4B5FD")

        res_dfs, res_bfs, summary_text = compare_algorithms(self.maze)
        self.latest_dfs_result = res_dfs
        self.latest_bfs_result = res_bfs

        # Update result cards
        self.update_dfs_card(res_dfs)
        self.update_bfs_card(res_bfs)

        # Update comparison text box
        self.summary_box.config(text=summary_text)
        self.lbl_detail_analysis.config(text=summary_text)

        # Update visualizer canvas with BFS result (shortest path)
        self.canvas_view.display_static_result(res_bfs)

        # Update Matplotlib comparison charts
        self.update_charts_display()

        if res_bfs.path_found:
            self._set_status("SOLVED", "#065F46", "#34D399")
        else:
            self._set_status("NO PATH", "#991B1B", "#FCA5A5")

    # =========================================================================
    # Results & Charts Updating
    # =========================================================================

    def update_dfs_card(self, res: SearchResult) -> None:
        """Update DFS card values."""
        found_txt = "Yes" if res.path_found else "No"
        len_txt = f"{res.path_length} steps" if res.path_length is not None else "N/A"
        self.lbl_dfs_path.config(text=f"Path Found: {found_txt}")
        self.lbl_dfs_nodes.config(text=f"Nodes Explored: {res.nodes_explored}")
        self.lbl_dfs_len.config(text=f"Path Length: {len_txt}")
        self.lbl_dfs_time.config(text=f"Execution Time: {res.execution_time_ms:.3f} ms")

    def update_bfs_card(self, res: SearchResult) -> None:
        """Update BFS card values."""
        found_txt = "Yes" if res.path_found else "No"
        len_txt = f"{res.path_length} steps" if res.path_length is not None else "N/A"
        self.lbl_bfs_path.config(text=f"Path Found: {found_txt}")
        self.lbl_bfs_nodes.config(text=f"Nodes Explored: {res.nodes_explored}")
        self.lbl_bfs_len.config(text=f"Path Length: {len_txt}")
        self.lbl_bfs_time.config(text=f"Execution Time: {res.execution_time_ms:.3f} ms")

    def reset_results_display(self) -> None:
        """Reset cards and charts to initial state."""
        self.latest_dfs_result = None
        self.latest_bfs_result = None
        for lbl in (self.lbl_dfs_path, self.lbl_dfs_nodes, self.lbl_dfs_len, self.lbl_dfs_time):
            lbl.config(text=lbl.cget("text").split(":")[0] + ": -")
        for lbl in (self.lbl_bfs_path, self.lbl_bfs_nodes, self.lbl_bfs_len, self.lbl_bfs_time):
            lbl.config(text=lbl.cget("text").split(":")[0] + ": -")
        self.summary_box.config(text="Ready. Select an algorithm to solve or click 'Compare Algorithms'.")
        self.lbl_detail_analysis.config(text="No comparative search performed yet. Run an algorithm or 'Compare Algorithms' to plot empirical results.")
        self.update_charts_display()

    def update_charts_display(self) -> None:
        """Refresh embedded Matplotlib figures."""
        render_comparison_charts(self.fig, self.latest_dfs_result, self.latest_bfs_result)
        self.canvas_chart.draw()

    def _on_close(self) -> None:
        """Safely clean up background tasks before exit."""
        self.canvas_view.stop_animation()
        self.destroy()


def main():
    """Application main entry point."""
    app = AIMazeSolverApp()
    app.mainloop()


if __name__ == "__main__":
    main()
