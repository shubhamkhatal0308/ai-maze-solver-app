"""
charts.py - Matplotlib Visual Analytics & Performance Comparison
================================================================
Artificial Intelligence Mini Project: AI Maze Solver & Route Visualizer
Experiment 13: Matplotlib Comparison Plots

This module generates three comparative analytical charts:
    1. Nodes Explored (DFS vs BFS)
    2. Path Length / Steps (DFS vs BFS)
    3. Execution Time in Milliseconds (DFS vs BFS)

Features:
    - Pure empirical measurements from real algorithm runs (no fake data).
    - Polished dark-theme styling matching the application aesthetic.
    - Handles "No Path" cases cleanly with descriptive annotations.
    - Embeddable into Tkinter via FigureCanvasTkAgg or exportable as images.
"""

import os
import tempfile
from typing import Optional

# Ensure Matplotlib config dir is writable on all Windows systems
if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "ai_maze_solver_mpl")

import matplotlib
matplotlib.use("Agg")  # Safe backend default; Tkinter canvas can still hook into FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from algorithms import SearchResult


# Modern Dark Theme Palette
DARK_BG = "#111827"        # Dark slate gray
CARD_BG = "#1F2937"        # Charcoal card background
TEXT_COLOR = "#F3F4F6"     # Off-white readable text
MUTED_TEXT = "#9CA3AF"     # Cool gray
GRID_COLOR = "#374151"     # Subtle grid lines
COLOR_DFS = "#EC4899"      # Rose / Pink for DFS
COLOR_BFS = "#3B82F6"      # Bright Blue for BFS


def create_comparison_figure() -> Figure:
    """
    Initialize a three-panel Matplotlib Figure styled with a dark theme.
    Returns:
        Figure: Configured Matplotlib figure with 3 subplots (1 row, 3 columns).
    """
    fig = Figure(figsize=(9.2, 3.2), dpi=100)
    fig.patch.set_facecolor(DARK_BG)
    fig.subplots_adjust(left=0.08, right=0.96, top=0.84, bottom=0.20, wspace=0.38)
    return fig


def style_axis(ax, title: str, ylabel: str) -> None:
    """Apply consistent dark styling, titles, and grid properties to an axis."""
    ax.set_facecolor(CARD_BG)
    ax.set_title(title, color=TEXT_COLOR, fontsize=11, fontweight="bold", pad=8)
    ax.set_ylabel(ylabel, color=TEXT_COLOR, fontsize=9)
    ax.tick_params(colors=MUTED_TEXT, labelsize=9)
    ax.grid(axis="y", color=GRID_COLOR, linestyle="--", linewidth=0.7, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)


def render_comparison_charts(
    fig: Figure,
    dfs_result: Optional[SearchResult],
    bfs_result: Optional[SearchResult],
    astar_result: Optional[SearchResult] = None,
) -> None:
    """
    Render or update the 3 comparison charts on the given figure.
    Supports individual algorithm runs or full multi-algorithm comparison.

    Args:
        fig (Figure): The Matplotlib figure to draw on.
        dfs_result (Optional[SearchResult]): DFS outcome data (or None).
        bfs_result (Optional[SearchResult]): BFS outcome data (or None).
        astar_result (Optional[SearchResult]): A* outcome data (or None).
    """
    fig.clear()
    axes = fig.subplots(1, 3)

    algorithms = ["DFS", "BFS"]
    bar_colors = [COLOR_DFS, COLOR_BFS]
    results = [dfs_result, bfs_result]

    if astar_result is not None or any(r is not None for r in [dfs_result, bfs_result]):
        algorithms = ["DFS", "BFS", "A*"]
        bar_colors = [COLOR_DFS, COLOR_BFS, "#8B5CF6"]
        results = [dfs_result, bfs_result, astar_result]

    # Handle initial state before any search runs
    if all(r is None for r in results):
        for ax, title, unit in zip(
            axes,
            ["Nodes Explored", "Path Length", "Execution Time"],
            ["Nodes", "Steps", "Time (ms)"]
        ):
            style_axis(ax, title, unit)
            ax.set_xticks(range(len(algorithms)))
            ax.set_xticklabels(algorithms)
            ax.set_ylim(0, 10)
            ax.text(
                0.5, 0.5, "Awaiting Search Data\nRun an algorithm or Compare",
                color=MUTED_TEXT, fontsize=9, ha="center", va="center",
                transform=ax.transAxes, style="italic"
            )
        return

    # Extract measured values
    node_vals = [r.nodes_explored if r else 0 for r in results]
    length_vals = [
        (r.path_length if (r and r.path_found and r.path_length is not None) else 0)
        for r in results
    ]
    time_vals = [r.execution_time_ms if r else 0.0 for r in results]

    # -------------------------------------------------------------------------
    # Chart 1: Nodes Explored
    # -------------------------------------------------------------------------
    ax1 = axes[0]
    style_axis(ax1, "Nodes Explored", "Total Nodes")
    bars1 = ax1.bar(algorithms, node_vals, color=bar_colors, width=0.55, edgecolor="#111827", linewidth=1.2)
    max_nodes = max(node_vals + [1])
    ax1.set_ylim(0, max_nodes * 1.25)
    for bar, val, res in zip(bars1, node_vals, results):
        label_text = f"{val}" if res is not None else "-"
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + (max_nodes * 0.03),
            label_text,
            ha="center", va="bottom", color=TEXT_COLOR, fontsize=9, fontweight="bold",
        )

    # -------------------------------------------------------------------------
    # Chart 2: Path Length (Steps)
    # -------------------------------------------------------------------------
    ax2 = axes[1]
    style_axis(ax2, "Path Length (Steps)", "Steps (len - 1)")
    bars2 = ax2.bar(algorithms, length_vals, color=bar_colors, width=0.55, edgecolor="#111827", linewidth=1.2)
    max_len = max(length_vals + [1])
    ax2.set_ylim(0, max_len * 1.25)

    for bar, val, res in zip(bars2, length_vals, results):
        if res is None:
            label_text = "-"
        elif res.path_found and res.path_length is not None:
            label_text = f"{val} steps"
        else:
            label_text = "No Path"
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + (max_len * 0.03),
            label_text,
            ha="center", va="bottom", color=TEXT_COLOR, fontsize=8.5, fontweight="bold",
        )

    # -------------------------------------------------------------------------
    # Chart 3: Execution Time (ms)
    # -------------------------------------------------------------------------
    ax3 = axes[2]
    style_axis(ax3, "Execution Time", "Milliseconds (ms)")
    bars3 = ax3.bar(algorithms, time_vals, color=bar_colors, width=0.55, edgecolor="#111827", linewidth=1.2)
    max_time = max(time_vals + [0.01])
    ax3.set_ylim(0, max_time * 1.30)
    for bar, val, res in zip(bars3, time_vals, results):
        label_text = f"{val:.3f} ms" if res is not None else "-"
        ax3.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + (max_time * 0.03),
            label_text,
            ha="center", va="bottom", color=TEXT_COLOR, fontsize=8.5, fontweight="bold",
        )
