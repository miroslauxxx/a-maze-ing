import random

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8
ALL_WALLS: int = NORTH | EAST | SOUTH | WEST


class MazeGenerationError(ValueError):
    """Exception used when maze generation parameters are invalid."""

    pass


class MazeGenerator:
    """Standalone, reusable maze generator supporting perfect and imperfect modes.

    Attributes:
        width: Horizontal dimension of the maze.
        height: Vertical dimension of the maze.
        perfect: If True, generates a tree maze with no loops. If False, generates Pac-Man style.
        seed: Random generator seed for reproducibility.
        entry: (x, y) coordinates of the entry point.
        exit: (x, y) coordinates of the exit point.
        maze: 2D list representing the grid of wall integers (0-15).
        blocked: Set of (x, y) coordinates forming the closed 42 pattern.
    """

    def __init__(
        self,
        width: int,
        height: int,
        perfect: bool = False,
        seed: int | None = None,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] | None = None,
    ) -> None:
        """Initialize the maze generator with parameters.

        Args:
            width: Width of the maze (columns).
            height: Height of the maze (rows).
            perfect: Whether the maze is single-path / loopless (True) or Pac-Man style (False).
            seed: Optional integer seed for reproducibility.
            entry: (x, y) coordinates of the starting cell.
            exit: (x, y) coordinates of the exit cell. Defaults to bottom-right corner.
        """
        self.width: int = width
        self.height: int = height
        self.perfect: bool = perfect
        self.seed: int | None = seed
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = (
            exit if exit is not None else (self.width - 1, self.height - 1)
        )

        self._rng: random.Random = random.Random(self.seed)
        self.maze: list[list[int]] = self.create_maze()
        self.blocked: set[tuple[int, int]] = self.create_42_cells()

        # Validate entry/exit don't collide with the blocked "42" pattern
        if self.entry in self.blocked:
            raise MazeGenerationError(
                f"ENTRY {self.entry} falls on a blocked '42' pattern cell. "
                f"Choose coordinates outside the pattern area."
            )
        if self.exit in self.blocked:
            raise MazeGenerationError(
                f"EXIT {self.exit} falls on a blocked '42' pattern cell. "
                f"Choose coordinates outside the pattern area."
            )
        if self.entry == self.exit:
            raise MazeGenerationError(
                f"ENTRY and EXIT cannot be identical: {self.entry}"
            )

    def create_maze(self) -> list[list[int]]:
        """Create an initial grid where all walls are fully closed (value 15).

        Returns:
            2D list of dimensions [height][width] filled with ALL_WALLS.
        """
        maze: list[list[int]] = []
        for _ in range(self.height):
            row: list[int] = [ALL_WALLS] * self.width
            maze.append(row)
        return maze

    def create_42_cells(self) -> set[tuple[int, int]]:
        """Build the set of cell coordinates that constitute the '42' pattern.

        If the dimensions are too small (< 9 wide or < 7 high), displays an error
        message and returns an empty set.

        Returns:
            Set of (x, y) tuples representing the blocked pattern cells.
        """
        pattern_width: int = 7
        pattern_height: int = 5

        if self.width < pattern_width + 2 or self.height < pattern_height + 2:
            print("Error: Maze is too small for the 42 pattern.")
            return set()

        pattern_cells: set[tuple[int, int]] = set()

        pattern_cells.add((0, 0))
        pattern_cells.add((2, 0))
        pattern_cells.add((0, 1))
        pattern_cells.add((2, 1))
        pattern_cells.add((0, 2))
        pattern_cells.add((1, 2))
        pattern_cells.add((2, 2))
        pattern_cells.add((2, 3))
        pattern_cells.add((2, 4))

        pattern_cells.add((4, 0))
        pattern_cells.add((5, 0))
        pattern_cells.add((6, 0))
        pattern_cells.add((6, 1))
        pattern_cells.add((6, 2))
        pattern_cells.add((5, 2))
        pattern_cells.add((4, 2))
        pattern_cells.add((4, 3))
        pattern_cells.add((4, 4))
        pattern_cells.add((5, 4))
        pattern_cells.add((6, 4))

        offset_x: int = (self.width - pattern_width) // 2
        offset_y: int = (self.height - pattern_height) // 2

        centered_cells: set[tuple[int, int]] = set()
        for x, y in pattern_cells:
            centered_cells.add((x + offset_x, y + offset_y))

        return centered_cells

    def remove_wall(self, x: int, y: int, direction: int) -> None:
        """Remove a wall between (x, y) and its neighbor in the given direction.

        Ensures bidirectional wall coherence between the two adjacent cells.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.
            direction: One of NORTH, EAST, SOUTH, WEST.
        """
        if direction == NORTH and y > 0:
            self.maze[y][x] &= ~NORTH
            self.maze[y - 1][x] &= ~SOUTH
        elif direction == EAST and x + 1 < self.width:
            self.maze[y][x] &= ~EAST
            self.maze[y][x + 1] &= ~WEST
        elif direction == SOUTH and y + 1 < self.height:
            self.maze[y][x] &= ~SOUTH
            self.maze[y + 1][x] &= ~NORTH
        elif direction == WEST and x > 0:
            self.maze[y][x] &= ~WEST
            self.maze[y][x - 1] &= ~EAST

    def add_wall(self, x: int, y: int, direction: int) -> None:
        """Add a wall between (x, y) and its neighbor in the given direction.

        Ensures bidirectional wall coherence.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.
            direction: One of NORTH, EAST, SOUTH, WEST.
        """
        if direction == NORTH and y > 0:
            self.maze[y][x] |= NORTH
            self.maze[y - 1][x] |= SOUTH
        elif direction == EAST and x + 1 < self.width:
            self.maze[y][x] |= EAST
            self.maze[y][x + 1] |= WEST
        elif direction == SOUTH and y + 1 < self.height:
            self.maze[y][x] |= SOUTH
            self.maze[y + 1][x] |= NORTH
        elif direction == WEST and x > 0:
            self.maze[y][x] |= WEST
            self.maze[y][x - 1] |= EAST

    def count_walls(self, x: int, y: int) -> int:
        """Count the number of active walls for cell (x, y).

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.

        Returns:
            Integer wall count (0 to 4).
        """
        cell: int = self.maze[y][x]
        return (
            bool(cell & NORTH)
            + bool(cell & EAST)
            + bool(cell & SOUTH)
            + bool(cell & WEST)
        )

    def get_neighbors(
        self,
        x: int,
        y: int,
        visited: set[tuple[int, int]],
    ) -> list[tuple[int, int, int]]:
        """Get unvisited and non-blocked neighbors of cell (x, y).

        Args:
            x: Current cell x-coordinate.
            y: Current cell y-coordinate.
            visited: Set of coordinates already visited in generation.

        Returns:
            List of tuples (nx, ny, direction) for eligible neighbors.
        """
        neighbors: list[tuple[int, int, int]] = []

        if (
            x + 1 < self.width
            and (x + 1, y) not in visited
            and (x + 1, y) not in self.blocked
        ):
            neighbors.append((x + 1, y, EAST))

        if (
            x - 1 >= 0
            and (x - 1, y) not in visited
            and (x - 1, y) not in self.blocked
        ):
            neighbors.append((x - 1, y, WEST))

        if (
            y + 1 < self.height
            and (x, y + 1) not in visited
            and (x, y + 1) not in self.blocked
        ):
            neighbors.append((x, y + 1, SOUTH))

        if (
            y - 1 >= 0
            and (x, y - 1) not in visited
            and (x, y - 1) not in self.blocked
        ):
            neighbors.append((x, y - 1, NORTH))

        return neighbors

    def is_valid_entry_or_exit(self, position: tuple[int, int]) -> bool:
        """Check if a position is a valid, unblocked coordinate within maze boundaries.

        Args:
            position: (x, y) tuple.

        Returns:
            True if position is within bounds and not blocked by the 42 pattern.
        """
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height and position not in self.blocked

    def check_entry_exit(self) -> bool:
        """Validate that both entry and exit are valid and distinct.

        Returns:
            True if valid, False otherwise.
        """
        return (
            self.is_valid_entry_or_exit(self.entry)
            and self.is_valid_entry_or_exit(self.exit)
            and self.entry != self.exit
        )

    def is_open_3x3(self, start_x: int, start_y: int) -> bool:
        """Check whether a 3x3 block starting at (start_x, start_y) is fully open.

        Args:
            start_x: Top-left x-coordinate of 3x3 block.
            start_y: Top-left y-coordinate of 3x3 block.

        Returns:
            True if there are no interior walls inside the 3x3 block.
        """
        for y in range(start_y, start_y + 3):
            for x in range(start_x, start_x + 2):
                if self.maze[y][x] & EAST:
                    return False
        for x in range(start_x, start_x + 3):
            for y in range(start_y, start_y + 2):
                if self.maze[y][x] & SOUTH:
                    return False
        return True

    def would_create_open_3x3(self, x: int, y: int, direction: int) -> bool:
        """Test if removing a wall would create a forbidden 3x3 open room.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.
            direction: Wall direction to test.

        Returns:
            True if an open 3x3 room would result, False otherwise.
        """
        self.remove_wall(x, y, direction)

        nx: int = x
        ny: int = y
        if direction == NORTH:
            ny -= 1
        elif direction == EAST:
            nx += 1
        elif direction == SOUTH:
            ny += 1
        elif direction == WEST:
            nx -= 1

        min_x: int = max(0, min(x, nx) - 2)
        max_x: int = min(self.width - 3, max(x, nx))
        min_y: int = max(0, min(y, ny) - 2)
        max_y: int = min(self.height - 3, max(y, ny))

        is_open: bool = False
        for start_y in range(min_y, max_y + 1):
            for start_x in range(min_x, max_x + 1):
                if self.is_open_3x3(start_x, start_y):
                    is_open = True
                    break
            if is_open:
                break

        self.add_wall(x, y, direction)
        return is_open

    def add_loops(self) -> int:
        """Add loops to the maze by removing walls at dead ends.

        Returns:
            Number of additional walls opened.
        """
        dead_ends: list[tuple[int, int]] = []
        opened_walls: int = 0

        for y in range(self.height):
            for x in range(self.width):
                if self.count_walls(x, y) == 3 and (x, y) not in self.blocked:
                    dead_ends.append((x, y))

        for x, y in dead_ends:
            if self.count_walls(x, y) != 3:
                continue

            candidates: list[int] = []
            if (
                self.maze[y][x] & EAST
                and x + 1 < self.width
                and (x + 1, y) not in self.blocked
            ):
                candidates.append(EAST)
            if (
                self.maze[y][x] & NORTH
                and y - 1 >= 0
                and (x, y - 1) not in self.blocked
            ):
                candidates.append(NORTH)
            if (
                self.maze[y][x] & WEST
                and x - 1 >= 0
                and (x - 1, y) not in self.blocked
            ):
                candidates.append(WEST)
            if (
                self.maze[y][x] & SOUTH
                and y + 1 < self.height
                and (x, y + 1) not in self.blocked
            ):
                candidates.append(SOUTH)

            if candidates:
                self._rng.shuffle(candidates)
                for direction in candidates:
                    if not self.would_create_open_3x3(x, y, direction):
                        self.remove_wall(x, y, direction)
                        opened_walls += 1
                        break

        return opened_walls

    def open_corners(self) -> None:
        """Open the inward walls at the four corners for Pac-Man style board."""
        corners: list[tuple[int, int]] = [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
        ]

        for x, y in corners:
            if x == 0 and x + 1 < self.width and (x + 1, y) not in self.blocked:
                self.remove_wall(x, y, EAST)
            elif x == self.width - 1 and x - 1 >= 0 and (x - 1, y) not in self.blocked:
                self.remove_wall(x, y, WEST)

            if y == 0 and y + 1 < self.height and (x, y + 1) not in self.blocked:
                self.remove_wall(x, y, SOUTH)
            elif y == self.height - 1 and y - 1 >= 0 and (x, y - 1) not in self.blocked:
                self.remove_wall(x, y, NORTH)

    def open_center(self) -> None:
        """Open central area passages for Pac-Man style board."""
        if self.blocked:
            offset_x: int = (self.width - 7) // 2
            offset_y: int = (self.height - 5) // 2
            center_x: int = offset_x + 3
            center_y: int = offset_y + 2

            if 0 <= center_x < self.width and 0 <= center_y < self.height:
                if center_y > 0 and (center_x, center_y - 1) not in self.blocked:
                    self.remove_wall(center_x, center_y, NORTH)
                if center_y + 1 < self.height and (center_x, center_y + 1) not in self.blocked:
                    self.remove_wall(center_x, center_y, SOUTH)
        else:
            center_x = self.width // 2
            center_y = self.height // 2
            if center_y > 0:
                self.remove_wall(center_x, center_y, NORTH)
            if center_y + 1 < self.height:
                self.remove_wall(center_x, center_y, SOUTH)

    def generate_maze(self) -> list[list[int]]:
        """Generate the maze layout using recursive backtracking and optional loops.

        Returns:
            The generated 2D maze wall matrix.
        """
        # Determine starting cell for DFS backtracker
        start_cell: tuple[int, int] = (
            self.entry if self.entry not in self.blocked else (0, 0)
        )
        if start_cell in self.blocked:
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) not in self.blocked:
                        start_cell = (x, y)
                        break
                if start_cell not in self.blocked:
                    break

        visited: set[tuple[int, int]] = {start_cell}
        stack: list[tuple[int, int]] = [start_cell]

        while stack:
            x, y = stack[-1]
            neighbors = self.get_neighbors(x, y, visited)

            if neighbors:
                nx, ny, direction = self._rng.choice(neighbors)
                self.remove_wall(x, y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        if not self.perfect:
            self.add_loops()
            self.open_corners()
            self.open_center()

        return self.maze

    def solve(self) -> list[tuple[int, int]]:
        """Find the shortest path coordinates from entry to exit.

        Returns:
            List of (x, y) coordinates.
        """
        from mazegen.solver import solve_maze

        path, _ = solve_maze(self.maze, self.width, self.height, self.entry, self.exit)
        return path

    def get_solution_path(self) -> list[tuple[int, int]]:
        """Return the shortest path coordinates from entry to exit."""
        return self.solve()

    def get_solution_directions(self) -> str:
        """Return the sequence of directions ('N', 'E', 'S', 'W') solving the maze."""
        from mazegen.solver import solve_maze

        _, directions = solve_maze(
            self.maze, self.width, self.height, self.entry, self.exit
        )
        return directions

    def check_wall_coherence(self) -> bool:
        """Verify that adjacent cells share identical wall states.

        Returns:
            True if all walls are coherent across the grid.
        """
        for y in range(self.height):
            for x in range(self.width):
                if x + 1 < self.width:
                    if bool(self.maze[y][x] & EAST) != bool(self.maze[y][x + 1] & WEST):
                        return False
                if y + 1 < self.height:
                    if bool(self.maze[y][x] & SOUTH) != bool(self.maze[y + 1][x] & NORTH):
                        return False
        return True

    def check_borders(self) -> bool:
        """Verify that all outer boundaries are closed.

        Returns:
            True if the outer perimeter is intact.
        """
        for x in range(self.width):
            if not (self.maze[0][x] & NORTH):
                return False
            if not (self.maze[self.height - 1][x] & SOUTH):
                return False

        for y in range(self.height):
            if not (self.maze[y][0] & WEST):
                return False
            if not (self.maze[y][self.width - 1] & EAST):
                return False

        return True

    def check_connectivity(self) -> bool:
        """Verify that all unblocked cells form a single connected component.

        Returns:
            True if all reachable cells equal total non-blocked cells.
        """
        start_cell: tuple[int, int] = (0, 0)
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.blocked:
                    start_cell = (x, y)
                    break
            if start_cell not in self.blocked:
                break

        visited: set[tuple[int, int]] = {start_cell}
        stack: list[tuple[int, int]] = [start_cell]

        while stack:
            x, y = stack.pop()
            moves: list[tuple[int, int, int]] = [
                (x + 1, y, EAST),
                (x - 1, y, WEST),
                (x, y + 1, SOUTH),
                (x, y - 1, NORTH),
            ]
            for nx, ny, wall in moves:
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and not (self.maze[y][x] & wall)
                    and (nx, ny) not in visited
                ):
                    visited.add((nx, ny))
                    stack.append((nx, ny))

        expected: int = self.width * self.height - len(self.blocked)
        return len(visited) == expected

    def check_no_loops(self) -> bool:
        """Verify that the maze has no cycles (tree structure).

        Returns:
            True if there are no loops, False if cycles exist.
        """
        start_cell: tuple[int, int] = (0, 0)
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.blocked:
                    start_cell = (x, y)
                    break
            if start_cell not in self.blocked:
                break

        visited: set[tuple[int, int]] = set()
        stack: list[tuple[tuple[int, int], tuple[int, int] | None]] = [(start_cell, None)]

        while stack:
            (x, y), parent = stack.pop()
            if (x, y) in visited:
                continue
            visited.add((x, y))

            moves: list[tuple[int, int, int]] = [
                (x, y - 1, NORTH),
                (x + 1, y, EAST),
                (x, y + 1, SOUTH),
                (x - 1, y, WEST),
            ]
            for nx, ny, wall in moves:
                if 0 <= nx < self.width and 0 <= ny < self.height and not (self.maze[y][x] & wall):
                    if (nx, ny) == parent:
                        continue
                    if (nx, ny) in visited:
                        return False
                    stack.append(((nx, ny), (x, y)))

        return True

    def count_dead_ends(self) -> int:
        """Count the number of dead-end cells in the maze (cells with 3 walls).

        Returns:
            Number of dead ends.
        """
        dead_ends: int = 0
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.blocked and self.count_walls(x, y) == 3:
                    dead_ends += 1
        return dead_ends

    def to_hex_grid(self) -> list[str]:
        """Convert the maze grid to hexadecimal representation strings per row.

        Returns:
            List of strings, one per row, each character representing a cell's walls in hex.
        """
        return ["".join(f"{cell:X}" for cell in row) for row in self.maze]

    def write_to_file(self, filename: str) -> None:
        """Save the maze and shortest path to a file according to project specs.

        Args:
            filename: Destination file path.
        """
        from mazegen.writer import write_maze_file

        write_maze_file(
            filename,
            self.maze,
            self.entry,
            self.exit,
            self.get_solution_directions(),
        )
