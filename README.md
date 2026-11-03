*This project has been created as part of the 42 curriculum by haschulz, milnicki*

# A-Maze-ing: Standalone Maze Generator, BFS Solver, & Terminal UI

A complete, robust, and extensible Python 3.10+ implementation of the 42 curriculum **A-Maze-ing** project. This repository features a standalone reusable maze generation and solving library (`mazegen`), compliant file format parsing and serialization, and a rich interactive Terminal User Interface (TUI) powered by Unicode box-drawing characters and ANSI color themes.

---

## Table of Contents
1. [Description](#description)
2. [Instructions & Quick Start](#instructions--quick-start)
3. [Module Usage Guide (`mazegen`)](#module-usage-guide-mazegen)
4. [Configuration Format Details](#configuration-format-details)
5. [Algorithm Justification](#algorithm-justification)
6. [Resources & AI Usage Disclosures](#resources--ai-usage-disclosures)
7. [Team Management Tracking](#team-management-tracking)
8. [License](#license)

---

## Description

A-Maze-ing is designed around three core pillars:
1. **The `mazegen` Reusable Library**: A standalone Python package installable via `pip` or wheel (`mazegen-1.0.0-py3-none-any.whl`) providing the `MazeGenerator` class, a BFS shortest-path solver (`solve_maze`), config parsing, and file writers.
2. **Dual-Mode Maze Architecture**:
   - **PERFECT = True (Academic Lab Maze)**: Generates a loopless spanning tree using Recursive Backtracking (DFS). Exactly one unique path exists between any two reachable cells.
   - **PERFECT = False (Pac-Man Board Style)**: Generates a fully connected maze featuring loops, an open center, open four corners, and minimized dead-ends, while strictly enforcing the rule against 3x3 open spaces.
   - **Mandatory "42" Pattern**: Embedded in the center of the maze as fully closed cells (value `15` / `0xF`) unless dimensions are smaller than 9x7 (handled gracefully with a descriptive warning).
   - **Wall Coherence**: Adjacent cells strictly share identical wall states (East-West and North-South), and outer borders are sealed.
3. **Interactive Terminal UI (TUI)**: The main entry point (`a_maze_ing.py`) provides clear, aligned rendering using Unicode box-drawing characters (`┌─┐│└┘┬┴├┤┼`), interactive menus, live regeneration, path toggling, and multi-color themes.

---

## Instructions & Quick Start

### Prerequisites
- Python 3.10 or newer (tested on Python 3.10 through 3.14)
- `make` utility

### Makefile Rules

| Command | Description |
| :--- | :--- |
| `make install` | Creates `.venv` (if not present) and installs dependencies + package |
| `make run` | Launches the interactive TUI application using `config.txt` |
| `make debug` | Runs the application with diagnostic assertions and metrics |
| `make lint` | Runs `flake8 .` and strict `mypy` checks |
| `make lint-strict` | Runs strict checks across all source files in the repository |
| `make build` | Builds the standalone wheel and source distribution in `dist/` |
| `make clean` | Cleans temporary caches, build artifacts, and output files |

### CLI Usage

```bash
# Run with default configuration (config.txt or config)
python3 a_maze_ing.py

# Run with a custom configuration file
python3 a_maze_ing.py my_config.txt

# Run in debug mode (prints wall coherence, border checks, connectivity)
python3 a_maze_ing.py config.txt --debug

# Run in non-interactive batch mode (renders once, writes output file, and exits)
python3 a_maze_ing.py config.txt --non-interactive
```

### Interactive Menu Controls
When running interactively, the runtime menu offers:
- `1`: **Re-generate a new maze**: Picks a fresh random seed, generates a new maze layout, solves it, updates the output file, and re-renders the grid.
- `2`: **Show/Hide the shortest path**: Toggles the visibility of the BFS solution path directly on the grid.
- `3`: **Change / Rotate wall colours**: Cycles through 5 ANSI palettes (Cyan Neon, Matrix Green, Cyberpunk Magenta, Solar Amber, Classic Monochrome).
- `4` (or `q` / `quit`): **Quit**: Cleanly exits the program.

---

## Module Usage Guide (`mazegen`)

The `mazegen` package is fully standalone and can be imported directly or installed into any Python environment:

```bash
# Install local wheel package
pip install dist/mazegen-1.0.0-py3-none-any.whl

# Or install in editable mode
pip install -e .
```

### Python API Example

```python
from mazegen import MazeGenerator, parse_config, solve_maze

# 1. Instantiate the generator
# Parameters: width, height, perfect, seed, entry, exit
generator = MazeGenerator(
    width=25,
    height=15,
    perfect=True,
    seed=42,
    entry=(0, 0),
    exit=(24, 14),
)

# 2. Generate the maze layout
maze_grid = generator.generate_maze()

# 3. Verify maze integrity
assert generator.check_wall_coherence() is True
assert generator.check_borders() is True
assert generator.check_connectivity() is True
assert generator.check_no_loops() is True  # True for perfect mazes

# 4. Access the grid structure (2D list of wall masks: North=1, East=2, South=4, West=8)
print("Row 0:", maze_grid[0])

# 5. Retrieve solution path and directional moves
path = generator.get_solution_path()            # List of (x, y) tuples
directions = generator.get_solution_directions()  # e.g. "EESEEENEES..."
print(f"Shortest path steps: {len(path)}, Directions: {directions}")

# 6. Save output formatted to specification
generator.write_to_file("maze.txt")
```

### Backward Compatibility
Legacy stub modules at the repository root remain intact and functional:
- `maze.py`: Exposes `MazeGenerator` and direction bitmasks (`NORTH`, `EAST`, `SOUTH`, `WEST`, `ALL_WALLS`).
- `solver.py`: Exposes `solve(generator)` and `solve_maze(...)`.
- `parses.py`: Exposes `Config`, `ConfigError`, and `parse_config(...)`.

---

## Configuration Format Details

### `config.txt` Syntax
The configuration file uses `KEY = VALUE` syntax. Empty lines and comment lines starting with `#` are ignored. Whitespace around keys and values is stripped automatically.

```ini
# A-Maze-ing Configuration
WIDTH = 25
HEIGHT = 15
ENTRY = 0,0
EXIT = 24,14
OUTPUT_FILE = maze.txt
PERFECT = True
SEED = 42
```

### Key Reference

| Key | Mandatory | Type | Description |
| :--- | :--- | :--- | :--- |
| `WIDTH` | Yes | Integer $\ge 3$ | Number of horizontal cells (columns) |
| `HEIGHT` | Yes | Integer $\ge 3$ | Number of vertical cells (rows) |
| `ENTRY` | Yes | `x,y` | Coordinates of start cell ($0 \le x < \text{WIDTH}, 0 \le y < \text{HEIGHT}$) |
| `EXIT` | Yes | `x,y` | Coordinates of exit cell ($0 \le x < \text{WIDTH}, 0 \le y < \text{HEIGHT}$) |
| `OUTPUT_FILE` | Yes | String | Destination path for serialized maze file |
| `PERFECT` | Yes | Boolean | `True` for academic lab maze (no loops); `False` for Pac-Man style |
| `SEED` | No | Integer | Seed for random number generator (for reproducibility) |

### Output File Format
The generated output file (`OUTPUT_FILE`) strictly complies with the project specifications:
1. **Lines 1 to HEIGHT**: Each line contains `WIDTH` hexadecimal characters representing wall bitmasks:
   - Bit 0 (`1`): North wall
   - Bit 1 (`2`): East wall
   - Bit 2 (`4`): South wall
   - Bit 3 (`8`): West wall
   - Cell value range: `0` (no walls) to `F` (`15`, completely closed cell).
2. **Line HEIGHT + 1**: An empty line separator.
3. **Line HEIGHT + 2**: Entry coordinates formatted as `x,y`.
4. **Line HEIGHT + 3**: Exit coordinates formatted as `x,y`.
5. **Line HEIGHT + 4**: Shortest path represented as a sequence of `N`, `E`, `S`, `W` directional characters.

---

## Algorithm Justification

### 1. Maze Generation: Recursive Backtracking (DFS)
- **Why DFS was chosen**:
  Recursive Backtracking (implemented iteratively via an explicit stack) produces mazes with a high "river" factor—long, winding corridors with fewer short dead ends compared to algorithms like Prim's or Kruskal's. This provides challenging, aesthetically pleasing mazes well suited for puzzle solving.
- **Complexity**:
  Explores each cell and edge at most once: time complexity is strictly $\mathcal{O}(V + E) = \mathcal{O}(W \times H)$, with memory complexity $\mathcal{O}(W \times H)$ for the stack and visited set.

### 2. Imperfect (Pac-Man Board Style) Transformation
- **Loop Creation**: In `PERFECT=False` mode, the algorithm identifies dead-end cells (cells with 3 closed walls) and selectively removes candidate walls into adjacent unblocked neighbors.
- **3x3 Open Space Prevention**: To adhere to Pac-Man arcade constraints where cavernous rooms are prohibited, `would_create_open_3x3` performs localized bounding-box checks prior to removing any wall. If removing a wall would create an open 3x3 square without interior walls, the wall is preserved.
- **Corners & Center**: The four corner cells have their inward walls opened, and the center gap in the 42 pattern is opened, replicating classic arcade navigation loops.

### 3. Maze Solver: Breadth-First Search (BFS)
- **Why BFS is optimal**:
  BFS explores grid cells in order of increasing distance from the entry point. On an unweighted 2D grid where each step has uniform cost, BFS is mathematically guaranteed to find the true shortest path without heuristic overhead.
- **Reconstruction**:
  Using a predecessor map (`parent`), the algorithm tracks the incoming direction (`N`, `E`, `S`, `W`) at each discovery step, allowing the optimal path and move string to be reconstructed in $\mathcal{O}(L)$ time (where $L$ is path length).

---

## Resources & AI Usage Disclosures

### References & Documentation
- Jamis Buck, *Mazes for Programmers: Code Your Own Twisty Little Passages*, Pragmatic Bookshelf.
- Unicode Standard, Box Drawing Block (`U+2500` through `U+257F`).
- Python Enhancement Proposals: PEP 8 (Style Guide), PEP 257 (Docstring Conventions), PEP 484 & PEP 561 (Type Hints & Package Typing).
- 42 Berlin Curriculum Project Specification: *A-Maze-ing*.

### AI Usage Disclosure
In compliance with 42 AI usage policies:
- Antigravity (Google DeepMind agentic coding assistant) was utilized during development for:
  - Codebase audit and refactoring legacy stubs (`maze.py`, `parses.py`, `solver.py`).
  - Strict type annotation and PEP 257 docstring compliance.
  - Designing the Unicode box-drawing vertex resolution algorithm.
  - Packaging structure (`pyproject.toml`, `setup.py`, wheel builds).
  - Makefile rule automation and test suite coverage.

---

## What Part of Your Code is Reusable, and How

The maze generation and solving logic is completely decoupled from the terminal UI and configuration files. It is packaged as a standalone Python library named `mazegen` (available at the root as `mazegen-1.0.0-py3-none-any.whl` and via standard `pip install`).

### Reusable Components:
1. **`mazegen.generator.MazeGenerator`**:
   - Primary reusable generator class supporting custom widths, heights, seeds, and entry/exit coordinates.
   - Generates both perfect mazes (spanning trees) and imperfect arcade boards (Pac-Man style).
   - Enforces wall coherence, outer borders, and the centered "42" pattern.
2. **`mazegen.solver.solve_maze` / `mazegen.solver.solve`**:
   - Universal BFS solver for any 2D maze wall matrix.
   - Computes shortest coordinate paths and directional strings (`N`, `E`, `S`, `W`).
3. **`mazegen.config.Config` / `mazegen.config.parse_config`**:
   - Modular key-value configuration parser and validator.
4. **`mazegen.writer.format_maze_output` / `mazegen.writer.write_maze_file`**:
   - Standardized maze serializer for output files.

Any future application (such as a 2D GUI, game engine, or web backend) can simply install the package and import these components without any reliance on `a_maze_ing.py`.

---

## Team Management Tracking

### 1. Team Roles
| Contributor | Role & Contributions |
| :--- | :--- |
| **Hanna Schulze (`haschulz`)** | Core recursive backtracking maze generation, 42 pattern definition, wall bitmask encoding, Pac-Man loop mechanics, BFS traversal logic. |
| **Miroslau Ilnicki (`milnicki`)** | Configuration parser design, syntax validation, input/output file formatting, initial repository setup. |
| **Antigravity (AI Assistant)** | Architecture integration into standalone `mazegen` package, TUI box-drawing renderer and ANSI color themes, strict typing, Makefile, and documentation. |

### 2. Anticipated Planning and Evolution
- **Initial Milestone**: Develop basic recursive backtracker and prototype config parser.
- **Midpoint Evolution**: Encountered loop and dead-end challenges in Pac-Man mode; realized that dead-end elimination required localized 3x3 open-space checks to avoid creating large empty rooms. BFS solver path reconstruction was completed.
- **Final Milestone**: Transitioned monolithic files into a modern, standalone reusable Python package (`mazegen`), structured standard pip builds (`pyproject.toml`), implemented ANSI/Unicode box-drawing TUI with live regeneration, and enforced strict type-safety with `mypy --strict`.

### 3. What Worked Well and What Could Be Improved
- **What Worked Well**:
  - Bitwise wall representation (`1`, `2`, `4`, `8`) made wall coherence checks and neighbor traversal clean and fast.
  - Stack-based iterative backtracker prevented recursion limit issues on large grids.
  - Decoupling the generator and solver into the `mazegen` library allowed thorough, isolated unit testing.
- **What Could Be Improved**:
  - Adding animation frames during generation (bonus feature) would make the visual representation even more engaging.
  - Expanding algorithm choices beyond DFS (e.g. Wilson's or Hunt-and-Kill) as additional modular generator strategies.

### 4. Tools Used
- **Python 3.10+** (Modern language features: union types `|`, dataclasses, match-case).
- **Flake8** for PEP 8 style conformance.
- **Mypy** for strict static type checking.
- **Pytest** for automated regression and edge-case testing.
- **Setuptools & Build** for standard wheel packaging.
- **Git** for version control and commit tracking.

---

## License

This project is licensed under the MIT License. See [LICENSE.md](file:///home/green/git/a/LICENSE.md) for full details.
