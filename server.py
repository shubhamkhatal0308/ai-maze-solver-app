"""
server.py - Local Web Server Runner
===================================
Runs the Flask application locally on port 5000.
"""

import os
from api.index import app

PORT = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    print(f"AI Maze Solver Server running at http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
