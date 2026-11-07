"""Breadth-First Search (BFS) shortest path solver module."""

from collections import deque
from typing import Any
from maze import EAST, NORTH, SOUTH, WEST
from mazegen.solver import solve_maze

__all__ = ["solve", "solve_maze"]


def solve(self: Any) -> list[tuple[int, int]]:
    """Solve the maze using Breadth-First Search (BFS).

    Args:
        self: A MazeGenerator instance providing entry, exit, maze, width, and height.

    Returns:
        List of (x, y) tuples representing the shortest path from entry to exit.
    """
    visited: set[tuple[int, int]] = set()

    queue: deque[tuple[int, int]] = deque([self.entry])

    parent: dict[tuple[int, int], tuple[int, int] | None] = {
        self.entry: None
    }

    visited.add(self.entry)

    while queue:
        x, y = queue.popleft()

        if (x, y) == self.exit:
            break

        neighbors: list[tuple[int, int]] = []

        if y > 0 and not (self.maze[y][x] & NORTH):
            neighbors.append((x, y - 1))

        if x + 1 < self.width and not (self.maze[y][x] & EAST):
            neighbors.append((x + 1, y))

        if y + 1 < self.height and not (self.maze[y][x] & SOUTH):
            neighbors.append((x, y + 1))

        if x > 0 and not (self.maze[y][x] & WEST):
            neighbors.append((x - 1, y))

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)

                parent[neighbor] = (x, y)

                queue.append(neighbor)

    if self.exit not in parent:
        return []

    path: list[tuple[int, int]] = []
    curr: tuple[int, int] | None = self.exit
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path
