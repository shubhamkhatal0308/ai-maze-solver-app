# AI Maze Solver & Route Visualizer
### *An Interactive Artificial Intelligence State Space Search & Empirical Comparison Platform*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter%20%26%20ttk-orange.svg)]()
[![Numerical](https://img.shields.io/badge/Matrix-NumPy-green.svg)](https://numpy.org/)
[![Plotting](https://img.shields.io/badge/Charts-Matplotlib-red.svg)](https://matplotlib.org/)
[![Tests](https://img.shields.io/badge/Tests-19%20Passed-brightgreen.svg)]()

---

## 📌 Project Overview
The **AI Maze Solver & Route Visualizer** is a comprehensive college-level Python Artificial Intelligence mini project. It provides an intuitive, interactive desktop environment for exploring, visualizing, and comparing classical **State Space Search** algorithms:
- **Depth First Search (DFS)** using a LIFO Stack
- **Breadth First Search (BFS)** using a FIFO Queue

The application features an interactive dark-themed desktop interface built with **Tkinter**, efficient 2D matrix representations using **NumPy**, non-blocking step-by-step search animations, and empirical performance analytics plotted with **Matplotlib**.

---

## 🔬 The Five Core AI Experiments Included
This project directly implements and satisfies five standard college AI laboratory experiments:
1. **Experiment 1 — State Space Search:** Formulates the 2D grid as a discrete state space where each state is a coordinate `(row, col)`, legal actions are cardinal steps (Up, Right, Down, Left), and transitions are validated against boundaries and obstacle walls.
2. **Experiment 4 — Depth First Search (DFS):** From-scratch stack-based implementation demonstrating deep branch exploration, backtracking, cycle prevention via visited sets, and path reconstruction.
3. **Experiment 5 — Breadth First Search (BFS):** From-scratch queue-based implementation using `collections.deque` demonstrating level-by-level exploration and guaranteeing shortest-path optimality on unweighted grids.
4. **Experiment 9 — NumPy Operations:** Utilizing NumPy 2D integer arrays (`dtype=np.int8`) for grid allocation, vectorized cell counting, wall density calculations, and stochastic corridor carving.
5. **Experiment 13 — Matplotlib Visualization:** Embedded dark-theme comparative bar charts graphing **Nodes Explored**, **Path Length (Steps)**, and **Execution Time (ms)** with microsecond accuracy via `time.perf_counter()`.

---

## ✨ Key Features
- **Modern Dark Theme Desktop GUI:** Polished slate/charcoal interface with intuitive controls, status badges, and responsive layout.
- **Interactive Mouse Drawing:** Click or drag with the mouse to draw or erase obstacle walls in real time.
- **Relocatable Start & Goal:** Switch mouse mode to "Set Start" or "Set Goal" to reposition endpoints anywhere on the grid.
- **Non-blocking Animation Engine:** Built on Tkinter's `.after()` scheduling to keep the GUI responsive during animated search without UI thread freezing.
- **Animation Speed Selector:** Choose between Slow (50ms), Normal (20ms), Fast (5ms), or Instant (0ms / skip animation).
- **Preset Demonstration Mazes:** Includes a handcrafted 15x15 demo preset specifically designed to illustrate how BFS finds a shorter path while DFS wanders into detours.
- **Solvable Random Maze Generator:** Configurable density algorithm that carves guaranteed corridors to ensure solvable demonstration mazes.
- **Side-by-Side Performance Analytics:** Real-time dual result cards and embedded Matplotlib charts comparing actual hardware metrics (no fabricated data).
- **Automated Path Validation:** Strict algorithmic validation checking start/goal endpoints, wall immunity, and absence of illegal diagonal or teleport jumps.
- **Full Test Coverage:** 19 automated unit tests verifying algorithms, maze constraints, and data visualizers.

---

## 🎨 Color Legend
| Item | Color Name | Hex Code | Visual Marker / Appearance |
| :--- | :--- | :--- | :--- |
| **Start State** | Vibrant Green | `#22C55E` | Letter **"S"** on green tile |
| **Goal State** | Vibrant Red | `#EF4444` | Letter **"G"** on red tile |
| **Wall / Obstacle** | Dark Slate | `#374151` | Solid dark gray block |
| **Empty Cell** | Light Gray | `#F3F4F6` | Open passable white/gray cell |
| **Explored Cell** | Soft Blue | `#60A5FA` | Visited / expanded state |
| **Final Path** | Vibrant Gold | `#FACC15` | Highlighted solution route |
| **Frontier** | Lavender Purple | `#C084FC` | Bordering frontier state |

---

## 📁 Project Directory Structure
```
ai_maze_solver/
│
├── main.py                     # Main application entry point & GUI integration
├── maze.py                     # Maze state space, NumPy matrices, & presets
├── algorithms.py               # Pure DFS & BFS algorithms, path validation, & timing
├── visualization.py            # Tkinter Canvas renderer & non-blocking animation
├── charts.py                   # Matplotlib comparative analytics (embedded FigureCanvasTkAgg)
├── requirements.txt            # External dependencies (numpy, matplotlib)
├── README.md                   # Comprehensive project guide & execution manual
├── .gitignore                  # Git exclusions for python caches & environments
│
├── tests/                      # Automated unit test suite (19 test cases)
│   ├── __init__.py             # Test package initializer
│   ├── test_algorithms.py      # DFS/BFS behavior, shortest path, & counter tests
│   ├── test_maze.py            # NumPy grid, dimension, & wall immunity tests
│   └── test_path_validation.py # Path integrity, diagonal rejection, & chart safety
│
└── docs/                       # College documentation & viva examination guides
    ├── project_report.md       # Full academic project report (21 sections)
    └── viva_questions.md       # 25 viva voce questions with student-friendly answers
```

---

## ⚙️ System Requirements
- **Operating System:** Windows 10/11, macOS 12+, or Linux
- **Python Version:** Python 3.10 or higher (Python 3.14 fully supported)
- **External Dependencies:** `numpy>=1.24.0`, `matplotlib>=3.7.0`
- **Standard Libraries Used:** `tkinter`, `collections`, `time`, `dataclasses`, `unittest`

---

## 🚀 Setup & Execution Guide (Windows)

### Step 1: Open Terminal / Command Prompt
Open PowerShell or Command Prompt and navigate to the project directory:
```powershell
cd C:\Users\shubh\.gemini\antigravity\scratch\ai_maze_solver
```

### Step 2: Create and Activate Virtual Environment (Recommended)
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Required Dependencies
Install the required packages using pip:
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Run the Application
Launch the desktop visualizer GUI:
```powershell
python main.py
```

---

## 🧪 Running Automated Tests
The project contains 19 thorough unit tests covering all required rubric points (TEST 1 through TEST 15).

Run all automated unit tests with verbose output:
```powershell
python -m unittest discover -s tests -v
```

### Expected Output:
```
test_test_12_bfs_optimality_compared_to_dfs ... ok
test_test_13_node_counters_consistency ... ok
test_test_1_bfs_shortest_path_open_grid ... ok
test_test_2_bfs_shortest_path_around_wall ... ok
test_test_3_dfs_valid_path_solvable_maze ... ok
test_test_4_disconnected_maze_reports_no_path ... ok
test_test_5_start_equals_goal_zero_steps ... ok
test_test_8_maze_immutability_during_searches ... ok
test_maze_clone_isolation ... ok
test_numpy_operations_analytics ... ok
test_preset_mazes ... ok
test_test_10_start_and_goal_cannot_be_walls ... ok
test_test_11_random_maze_generation_shape_and_values ... ok
test_test_9_invalid_dimensions_rejected ... ok
test_test_14_project_imports_successfully ... ok
test_test_15_comparison_and_charts_handle_no_path_case ... ok
test_test_6_returned_paths_never_cross_walls ... ok
test_test_7_returned_paths_only_contain_legal_adjacent_moves ... ok
test_validate_path_endpoint_checks ... ok

----------------------------------------------------------------------
Ran 19 tests in 0.242s

OK
```

---

## 🎮 Step-by-Step Usage Guide for Classroom Demonstration

1. **Demonstrating DFS (Depth First Search):**
   - Click the **"Demo Preset"** button to load the handcrafted 15x15 maze.
   - Click **"▶ Run DFS"**.
   - Observe how DFS follows a single corridor deeply before backtracking.
   - Note the resulting path length and nodes explored on the DFS card.

2. **Demonstrating BFS (Breadth First Search):**
   - Click **"Reset Search"** to clear the trail while keeping the walls intact.
   - Click **"▶ Run BFS"**.
   - Observe how BFS ripples outward level-by-level in concentric rings.
   - Note that BFS returns the **optimal shortest path**.

3. **Demonstrating Empirical Comparison & Charts:**
   - Click **"⚡ Compare Algorithms"**.
   - The system executes both algorithms independently on exact clones of the maze.
   - The result cards and summary text update with the exact measured differences.
   - Switch to the **"Performance Comparison Charts"** tab to view the three Matplotlib bar charts comparing **Nodes Explored**, **Path Length**, and **Execution Time**.

4. **Demonstrating Interactive Wall Editing:**
   - Select the **"Wall Draw/Erase"** radio button.
   - Click and drag across the maze canvas to build custom barriers or carve openings.
   - Run DFS or BFS to see how the algorithms navigate your custom layout.

5. **Demonstrating Unreachable Goal Handling:**
   - Draw a solid wall completely cutting off the Goal from the Start.
   - Click **"▶ Run BFS"** or **"Compare Algorithms"**.
   - Notice that the status changes to **"NO PATH"** in red, and the chart cleanly displays **"No Path"** without errors or misleading zero-step values.

---

## ❓ Troubleshooting
- **Issue:** Tkinter displays an error about `_tkinter` not found.  
  **Solution:** Ensure you are using a standard desktop distribution of Python that includes Tk/Tcl support (standard Python installer for Windows includes Tkinter by default).
- **Issue:** Matplotlib displays a warning regarding cache directory permissions on Windows.  
  **Solution:** The application automatically sets `MPLCONFIGDIR` to a safe writable temporary folder (`%TEMP%\ai_maze_solver_mpl`) at runtime.
- **Issue:** Tests cannot find module `maze`.  
  **Solution:** Run tests from the root `ai_maze_solver` directory using `python -m unittest discover -s tests -v`.

---

## 🎓 Academic Documentation
Comprehensive reports prepared for faculty evaluation and viva defense are located in `docs/`:
- **`docs/project_report.md`**: Complete 21-section academic report with abstract, architecture diagrams, flowcharts, complexity analysis, and references.
- **`docs/viva_questions.md`**: 25 questions with clear, comprehensive answers covering state spaces, DFS vs BFS mechanics, NumPy operations, time/space complexity, and viva tips.

---

## 📜 License
Developed as an educational Artificial Intelligence mini project for academic coursework and laboratory demonstration. Open source under the MIT License.
