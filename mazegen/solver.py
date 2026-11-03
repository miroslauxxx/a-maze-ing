"""BFS-based maze solver module for finding shortest solution paths."""

from collections import deque
from typing import Any, Sequence

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8


def solve_maze(
    maze: Sequence[Sequence[int]],
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
) -> tuple[list[tuple[int, int]], str]:
    """Find the shortest path from entry to exit using Breadth-First Search (BFS).

    Args:
        maze: 2D grid representing wall states.
        width: Grid width.
        height: Grid height.
        entry: (x, y) starting coordinate.
        exit_pos: (x, y) target exit coordinate.

    Returns:
        A tuple containing:
            - List of (x, y) coordinates representing the path from entry to exit.
            - String containing directional moves ('N', 'E', 'S', 'W').
    """
    if entry == exit_pos:
        return [entry], ""

    visited: set[tuple[int, int]] = {entry}
    queue: deque[tuple[int, int]] = deque([entry])
    parent: dict[tuple[int, int], tuple[tuple[int, int], str] | None] = {entry: None}

    found: bool = False
    while queue:
        x, y = queue.popleft()
        if (x, y) == exit_pos:
            found = True
            break

        moves: list[tuple[int, int, int, str]] = [
            (x, y - 1, NORTH, "N"),
            (x + 1, y, EAST, "E"),
            (x, y + 1, SOUTH, "S"),
            (x - 1, y, WEST, "W"),
        ]

        for nx, ny, wall_mask, move_char in moves:
            if 0 <= nx < width and 0 <= ny < height:
                if not (maze[y][x] & wall_mask) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = ((x, y), move_char)
                    queue.append((nx, ny))

    if not found or exit_pos not in parent:
        return [], ""

    path: list[tuple[int, int]] = []
    directions: list[str] = []
    curr: tuple[int, int] = exit_pos

    while True:
        info = parent[curr]
        if info is None:
            break
        path.append(curr)
        prev, move = info
        directions.append(move)
        curr = prev

    path.append(entry)
    path.reverse()
    directions.reverse()

    return path, "".join(directions)


def solve(generator: Any) -> list[tuple[int, int]]:
    """Solve the maze for a MazeGenerator instance.

    Args:
        generator: An instance providing width, height, entry, exit, and maze attributes.

    Returns:
        A list of (x, y) coordinates representing the shortest path.
    """
    path, _ = solve_maze(
        generator.maze,
        generator.width,
        generator.height,
        generator.entry,
        generator.exit,
    )
    return path
