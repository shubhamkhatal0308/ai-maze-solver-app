"""
app.py - Main Web Application Entry Point
==========================================
Imports the Flask application from api/index.py for local execution or WSGI servers.
"""

import os
from api.index import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting AI Maze Solver at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
