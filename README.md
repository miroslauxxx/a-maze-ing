_This project has been created as part of the 42 curriculum by haschulz, milnicki_

## Description
It's a maze generator in Python that takes a configuration file, generates
a maze, possibly perfect (with a single path between entrance and exit), and 
writes it to a file using a hexadecimal wall representation. Maze algorithm 
implemented and code organized so that the generation logic can be reused.

### Instructions

| Command | Description |
| :--- | :--- |
| `make install` | Creates `.venv` (if not present) and installs dependencies + package |
| `make run` | Launches the application using `config.txt` |
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

# Run in non-interactive batch mode (renders once, writes output file, and exits)
python3 a_maze_ing.py config.txt --non-interactive
```
---

## Module Usage Guide (`mazegen`)

The `mazegen` package is fully standalone and can be imported directly or installed into any Python environment:

```bash
# Install local wheel package
pip install mazegen-1.0.0-py3-none-any.whl
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

# 3. Access the grid structure (2D list of wall masks: North=1, East=2, South=4, West=8)
print("Row 0:", maze_grid[0])

# 4. Retrieve solution path and directional moves
path = generator.get_solution_path()            # List of (x, y) tuples
directions = generator.get_solution_directions()  # e.g. "EESEEENEES..."
print(f"Shortest path steps: {len(path)}, Directions: {directions}")

# 5. Save output formatted to specification
generator.write_to_file("maze.txt")
```
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

WIDTH Number of horizontal cells (columns)
HEIGHT Number of vertical cells (rows) 
ENTRY Coordinates of start cell 
EXIT Coordinates of exit cell
OUTPUT\_FILE Destination path for serialized maze file 
PERFECT True for academic lab maze (no loops) False for Pac-Man style
SEED Seed for random number generator (for reproducibility) 

### Output File Format
The generated output file (`OUTPUT_FILE`) strictly complies with the project specifications:
1. Lines 1 to HEIGHT: Each line contains `WIDTH` hexadecimal characters representing wall bitmasks:
    Cell value range: 0 (no walls) to F (closed)
2. Line HEIGHT + 1 An empty line separator
3. Line HEIGHT + 2 Entry coordinates formatted as x,y
4. Line HEIGHT + 3 Exit coordinates formatted as x,y
5. Line HEIGHT + 4 Shortest path represented as a sequence of N, E, S, W directional characters.

---

## Algorithm Justification

### 1. Maze Generation: Recursive Backtracking (DFS)
- Why DFS was chosen:
  Recursive Backtracking produces mazes with a high "river" factor—long, winding corridors with fewer short dead ends compared to algorithms like Prim's or Kruskal's. This provides challenging, aesthetically pleasing mazes well suited for puzzle solving.

### 2. Imperfect (Pac-Man Board Style) Transformation
- Loop Creation: In PERFECT=False mode, the algorithm identifies dead-end cells (cells with 3 closed walls) and selectively removes candidate walls into adjacent unblocked neighbors.
- 3x3 Open Space Prevention: To adhere to Pac-Man arcade constraints where cavernous rooms are prohibited, would\_create\_open\_3x3 performs localized bounding-box checks prior to removing any wall. If removing a wall would create an open 3x3 square without interior walls, the wall is preserved.
- Corners & Center: The four corner cells have their inward walls opened, and the center gap in the 42 pattern is opened, replicating classic arcade navigation loops.

### 3. Maze Solver: BFS (Breadth-First Search)
- Why BFS is optimal:
  BFS explores grid cells in order of increasing distance from the entry point. On an unweighted 2D grid where each step has uniform cost, BFS is mathematically guaranteed to find the true shortest path without overhead.
- Reconstruction:
  Using a predecessor map parent, the algorithm tracks the incoming direction (N, E, S, W) at each discovery step, allowing the optimal path and move string to be reconstructed in $\mathcal{O}(L)$ time (where $L$ is path length).

---

## Resources & AI Usage Disclosures

### References & Documentation
- Jamis Buck, *Mazes for Programmers: Code Your Own Twisty Little Passages*, Pragmatic Bookshelf.
- Python Enhancement Proposals: PEP 8 (Style Guide), PEP 257 (Docstring Conventions), PEP 484 & PEP 561 (Type Hints & Package Typing).

### AI Usage Disclosure
In compliance with 42 AI usage policies:
- Antigravity (Google DeepMind agentic coding assistant) was utilized during development for:
  - Codebase audit and refactoring legacy stubs 
  - Strict type annotation and PEP 257 docstring compliance.
  - Designing the Unicode box-drawing vertex resolution algorithm.
  - Packaging structure (`pyproject.toml`, `setup.py`, wheel builds).
  - Makefile rule review

---
## Team Management Tracking

### 1. Team Roles
haschulz: Core recursive backtracking maze generation, 42 pattern definition, wall bitmask encoding, Pac-Man loop mechanics, BFS traversal logic.
milnicki: Configuration parser design, syntax validation, input/output file formatting, initial repository setup.

### 2. Anticipated Planning and Evolution
1. Develop basic recursive backtracker and prototype config parser.
2. Encountered loop and dead-end challenges in Pac-Man mode; realized that dead-end elimination required localized 3x3 open-space checks to avoid creating large empty rooms. BFS solver path reconstruction was completed.
3. Transitioned monolithic files into a modern, standalone reusable Python package (`mazegen`), structured standard pip builds (`pyproject.toml`), implemented ANSI/Unicode box-drawing TUI with live regeneration, and enforced strict type-safety with `mypy --strict`.

### 3. What Worked Well and What Could Be Improved
What Worked Well:
  - Bitwise wall representation (`1`, `2`, `4`, `8`) made wall coherence checks and neighbor traversal clean and fast.
  - Stack-based iterative backtracker prevented recursion limit issues on large grids.
  - Decoupling the generator and solver into the `mazegen` library allowed thorough, isolated unit testing.
What Could Be Improved:
  - Adding animation frames during generation (bonus feature) would make the visual representation even more engaging.
  - Expanding algorithm choices beyond DFS (e.g. Wilson's or Hunt-and-Kill) as additional modular generator strategies.

### 4. Tools Used
- Python 3.10+ 
- Flake8 & Mypy 
- Setuptools & Build for standard wheel packaging.

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for full details.
