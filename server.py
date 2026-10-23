"""
server.py - Lightweight Local Web Server & REST API
===================================================
Artificial Intelligence Mini Project: AI Maze Solver & Route Visualizer
Provides an interactive web frontend accessible at http://localhost:5000

Features:
    - Pure standard library Python HTTP server (0 extra dependencies).
    - Serves static interactive HTML5/Canvas UI from web/index.html.
    - REST Endpoints:
        POST /api/generate: Create preset or random solvable mazes.
        POST /api/solve: Execute DFS, BFS, or A* on current grid.
        POST /api/compare: Run DFS, BFS, and A* in parallel and return metrics.
"""

import http.server
import json
import os
import socketserver
import sys
from typing import Tuple
import numpy as np

# Ensure project modules are importable
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from maze import Maze
from algorithms import dfs, bfs, astar, SearchResult, validate_path


PORT = 5000


class MazeRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handles static web requests and algorithm REST API calls."""

    def __init__(self, *args, **kwargs):
        # Serve static files from web/ directory
        super().__init__(*args, directory=os.path.join(PROJECT_DIR, "web"), **kwargs)

    def do_POST(self):
        """Handle algorithm execution and maze generation API endpoints."""
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            req_json = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            self._send_json({"error": "Malformed JSON payload"}, status=400)
            return

        if self.path == "/api/generate":
            self._handle_generate(req_json)
        elif self.path == "/api/solve":
            self._handle_solve(req_json)
        elif self.path == "/api/compare":
            self._handle_compare(req_json)
        else:
            self._send_json({"error": f"Unknown endpoint: {self.path}"}, status=404)

    def _send_json(self, data: dict, status: int = 200) -> None:
        """Send a JSON HTTP response."""
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def _handle_generate(self, req: dict) -> None:
        """Generate a preset or random solvable maze."""
        preset = req.get("preset")
        if preset:
            try:
                maze = Maze.create_preset(preset)
            except Exception:
                maze = Maze.create_preset("demo_15x15")
        else:
            rows = int(req.get("rows", 15))
            cols = int(req.get("cols", 15))
            density = float(req.get("density", 0.28))
            seed = req.get("seed")
            solvable = bool(req.get("guarantee_solvable", True))
            maze = Maze(rows=rows, cols=cols)
            maze.generate_random(density=density, seed=seed, guarantee_solvable=solvable)

        self._send_json({
            "rows": maze.rows,
            "cols": maze.cols,
            "grid": maze.grid.tolist(),
            "start": list(maze.start),
            "goal": list(maze.goal),
            "wall_count": maze.wall_count(),
            "open_count": maze.open_count(),
            "wall_density_pct": round(maze.wall_density(), 2),
        })

    def _handle_solve(self, req: dict) -> None:
        """Execute a single search algorithm on provided maze state."""
        algo = req.get("algorithm", "BFS").upper()
        raw_grid = req.get("grid")
        start = tuple(req.get("start", [0, 0]))
        goal = tuple(req.get("goal", [14, 14]))

        if not raw_grid:
            self._send_json({"error": "Grid is required"}, status=400)
            return

        grid_arr = np.array(raw_grid, dtype=np.int8)
        maze = Maze(rows=grid_arr.shape[0], cols=grid_arr.shape[1], start=start, goal=goal, grid=grid_arr)

        if algo == "DFS":
            result = dfs(maze)
        elif algo == "ASTAR" or algo == "A*":
            result = astar(maze)
        else:
            result = bfs(maze)

        self._send_json({
            "algorithm": result.algorithm,
            "path_found": result.path_found,
            "path": result.path,
            "nodes_explored": result.nodes_explored,
            "path_length": result.path_length,
            "execution_time_ms": result.execution_time_ms,
            "exploration_order": result.exploration_order,
            "status_message": result.status_message,
        })

    def _handle_compare(self, req: dict) -> None:
        """Run DFS, BFS, and A* on the current maze and produce comparative statistics."""
        raw_grid = req.get("grid")
        start = tuple(req.get("start", [0, 0]))
        goal = tuple(req.get("goal", [14, 14]))

        if not raw_grid:
            self._send_json({"error": "Grid is required"}, status=400)
            return

        grid_arr = np.array(raw_grid, dtype=np.int8)
        maze = Maze(rows=grid_arr.shape[0], cols=grid_arr.shape[1], start=start, goal=goal, grid=grid_arr)

        res_dfs = dfs(maze.clone())
        res_bfs = bfs(maze.clone())
        res_astar = astar(maze.clone())

        # Generate comparative summary
        lines = []
        lines.append(f"Grid: {maze.rows}x{maze.cols} | Obstacle Density: {maze.wall_density():.1f}%")
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

        self._send_json({
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


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_server(port: int = PORT):
    """Launch the HTTP server."""
    with ReusableTCPServer(("", port), MazeRequestHandler) as httpd:
        print(f"AI Maze Solver Server running at http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.server_close()


if __name__ == "__main__":
    start_server(PORT)
