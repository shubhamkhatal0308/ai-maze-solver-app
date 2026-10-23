"""
api/index.py - Vercel Serverless Entry Point & Flask REST API
============================================================
Exposes the WSGI `app` callable required by Vercel's Python runtime.
Serves the HTML5 maze visualizer at '/' and provides API endpoints for
maze generation, single-algorithm search, and multi-algorithm comparisons.
"""

import os
import sys
from typing import Dict, Any
from flask import Flask, request, jsonify, Response
import numpy as np

# Ensure project root directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from maze import Maze
from algorithms import dfs, bfs, astar, SearchResult, validate_path

app = Flask(
    __name__,
    template_folder=os.path.join(CURRENT_DIR, "templates"),
    static_folder=os.path.join(ROOT_DIR, "public"),
)


def get_index_html() -> str:
    """
    Load index.html from multiple fallback locations:
    1. api/templates/index.html (guaranteed to be packaged by Vercel inside api/ directory)
    2. templates/index.html
    3. public/index.html
    4. web/index.html
    """
    candidates = [
        os.path.join(CURRENT_DIR, "templates", "index.html"),
        os.path.join(ROOT_DIR, "templates", "index.html"),
        os.path.join(ROOT_DIR, "public", "index.html"),
        os.path.join(ROOT_DIR, "web", "index.html"),
        os.path.join(os.getcwd(), "public", "index.html"),
        os.path.join(os.getcwd(), "web", "index.html"),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
    return "<!DOCTYPE html><html><body><h1>AI Maze Solver & Route Visualizer</h1><p>UI loading error.</p></body></html>"


@app.after_request
def add_cors_headers(response: Response) -> Response:
    """Enable CORS headers for all requests."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# Root and static routes
@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
@app.route("/api", methods=["GET"])
@app.route("/api/", methods=["GET"])
@app.route("/api/index.py", methods=["GET"])
def index():
    """Serve the interactive HTML5/Canvas maze solver application."""
    html = get_index_html()
    return Response(html, mimetype="text/html")


@app.route("/api/generate", methods=["POST", "OPTIONS"])
@app.route("/generate", methods=["POST", "OPTIONS"])
def generate():
    """Generate a preset or random solvable maze using the NumPy Maze class."""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    preset = payload.get("preset")

    if preset:
        try:
            maze = Maze.create_preset(preset)
        except Exception:
            maze = Maze.create_preset("demo_15x15")
    else:
        rows = int(payload.get("rows", 15))
        cols = int(payload.get("cols", 15))
        density = float(payload.get("density", 0.28))
        seed = payload.get("seed")
        solvable = bool(payload.get("guarantee_solvable", True))
        maze = Maze(rows=rows, cols=cols)
        maze.generate_random(density=density, seed=seed, guarantee_solvable=solvable)

    return jsonify({
        "rows": maze.rows,
        "cols": maze.cols,
        "grid": maze.grid.tolist(),
        "start": list(maze.start),
        "goal": list(maze.goal),
        "wall_count": maze.wall_count(),
        "open_count": maze.open_count(),
        "wall_density_pct": round(maze.wall_density(), 2),
    })


@app.route("/api/solve", methods=["POST", "OPTIONS"])
@app.route("/solve", methods=["POST", "OPTIONS"])
def solve():
    """Execute DFS, BFS, or A* on the supplied maze grid."""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    algo = payload.get("algorithm", "BFS").upper()
    raw_grid = payload.get("grid")
    start = tuple(payload.get("start", [0, 0]))
    goal = tuple(payload.get("goal", [14, 14]))

    if not raw_grid:
        return jsonify({"error": "Grid matrix is required"}), 400

    grid_arr = np.array(raw_grid, dtype=np.int8)
    maze = Maze(rows=grid_arr.shape[0], cols=grid_arr.shape[1], start=start, goal=goal, grid=grid_arr)

    if algo == "DFS":
        result: SearchResult = dfs(maze)
    elif algo in ("ASTAR", "A*"):
        result = astar(maze)
    else:
        result = bfs(maze)

    return jsonify({
        "algorithm": result.algorithm,
        "path_found": result.path_found,
        "path": result.path,
        "nodes_explored": result.nodes_explored,
        "path_length": result.path_length,
        "execution_time_ms": result.execution_time_ms,
        "exploration_order": result.exploration_order,
        "status_message": result.status_message,
    })


@app.route("/api/compare", methods=["POST", "OPTIONS"])
@app.route("/compare", methods=["POST", "OPTIONS"])
def compare():
    """Run DFS, BFS, and A* simultaneously on the maze and return comparison metrics."""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    raw_grid = payload.get("grid")
    start = tuple(payload.get("start", [0, 0]))
    goal = tuple(payload.get("goal", [14, 14]))

    if not raw_grid:
        return jsonify({"error": "Grid matrix is required"}), 400

    grid_arr = np.array(raw_grid, dtype=np.int8)
    maze = Maze(rows=grid_arr.shape[0], cols=grid_arr.shape[1], start=start, goal=goal, grid=grid_arr)

    res_dfs = dfs(maze.clone())
    res_bfs = bfs(maze.clone())
    res_astar = astar(maze.clone())

    lines = [f"Grid: {maze.rows}x{maze.cols} | Obstacle Density: {maze.wall_density():.1f}%"]
    if res_bfs.path_found:
        lines.append("• Route Status: Path found by all algorithms.")
        if res_dfs.path_length and res_bfs.path_length:
            if res_bfs.path_length < res_dfs.path_length:
                lines.append(f"• Path Length: BFS & A* found the optimal path ({res_bfs.path_length} steps vs DFS {res_dfs.path_length} steps).")
            else:
                lines.append(f"• Path Length: All found paths of {res_bfs.path_length} steps.")
        lines.append(f"• Exploration: A* explored {res_astar.nodes_explored} nodes | BFS explored {res_bfs.nodes_explored} nodes | DFS explored {res_dfs.nodes_explored} nodes.")
        lines.append(f"• Runtimes: DFS: {res_dfs.execution_time_ms:.3f}ms | BFS: {res_bfs.execution_time_ms:.3f}ms | A*: {res_astar.execution_time_ms:.3f}ms")
    else:
        lines.append("• Route Status: Goal is unreachable. No path found.")

    return jsonify({
        "dfs": {
            "algorithm": res_dfs.algorithm,
            "path_found": res_dfs.path_found,
            "path": res_dfs.path,
            "nodes_explored": res_dfs.nodes_explored,
            "path_length": res_dfs.path_length,
            "execution_time_ms": res_dfs.execution_time_ms,
            "exploration_order": res_dfs.exploration_order,
        },
        "bfs": {
            "algorithm": res_bfs.algorithm,
            "path_found": res_bfs.path_found,
            "path": res_bfs.path,
            "nodes_explored": res_bfs.nodes_explored,
            "path_length": res_bfs.path_length,
            "execution_time_ms": res_bfs.execution_time_ms,
            "exploration_order": res_bfs.exploration_order,
        },
        "astar": {
            "algorithm": res_astar.algorithm,
            "path_found": res_astar.path_found,
            "path": res_astar.path,
            "nodes_explored": res_astar.nodes_explored,
            "path_length": res_astar.path_length,
            "execution_time_ms": res_astar.execution_time_ms,
            "exploration_order": res_astar.exploration_order,
        },
        "summary": "\n".join(lines),
    })


@app.route("/<path:path>", methods=["GET"])
def fallback(path):
    """Fallback route for any static asset or URL rewrite."""
    for folder in [os.path.join(ROOT_DIR, "public"), os.path.join(ROOT_DIR, "web")]:
        candidate = os.path.join(folder, path)
        if os.path.exists(candidate) and not os.path.isdir(candidate):
            with open(candidate, "rb") as f:
                return Response(f.read())
    return Response(get_index_html(), mimetype="text/html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
