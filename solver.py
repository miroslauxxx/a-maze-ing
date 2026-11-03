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
    # Hier speichern wir alle Zellen, die wir bereits besucht haben.
    # Am Anfang haben wir noch keine Zelle besucht -> leeres Set.
    visited: set[tuple[int, int]] = set()

    # Das ist unsere Warteschlange (Queue) für BFS.
    # Zu Beginn befindet sich nur der Entry darin.
    #
    # Beispiel:
    # self.entry = (0, 0)
    # queue = deque([(0, 0)])
    queue: deque[tuple[int, int]] = deque([self.entry])

    # Hier merken wir uns später, von welcher Zelle wir
    # zu einer bestimmten Zelle gekommen sind.
    #
    # Beim Entry gibt es keinen Vorgänger, deshalb None.
    #
    # Beispiel:
    # {
    #     (0, 0): None
    # }
    parent: dict[tuple[int, int], tuple[int, int] | None] = {
        self.entry: None
    }

    # Den Entry markieren wir direkt als besucht.
    # Dadurch verhindern wir, dass wir ihn später nochmal
    # in die Queue packen.
    visited.add(self.entry)

    # Solange noch Zellen in der Queue liegen,
    # gibt es noch Zellen, die BFS untersuchen soll.
    while queue:
        # Nimm die ÄLTESTE Zelle aus der Queue.
        #
        # popleft() ist wichtig für BFS.
        #
        # Beispiel:
        # queue = [(0, 0), (1, 0), (0, 1)]
        #
        # popleft() gibt (0, 0)
        # queue danach = [(1, 0), (0, 1)]
        x, y = queue.popleft()

        # Haben wir den Exit erreicht?
        if (x, y) == self.exit:
            # Ja -> wir müssen nicht weitersuchen.
            break

        # Erreichbare Nachbarn sammeln
        neighbors: list[tuple[int, int]] = []

        # NORTH
        if y > 0 and not (self.maze[y][x] & NORTH):
            neighbors.append((x, y - 1))

        # EAST
        if x + 1 < self.width and not (self.maze[y][x] & EAST):
            neighbors.append((x + 1, y))

        # SOUTH
        if y + 1 < self.height and not (self.maze[y][x] & SOUTH):
            neighbors.append((x, y + 1))

        # WEST
        if x > 0 and not (self.maze[y][x] & WEST):
            neighbors.append((x - 1, y))

        # Neue Nachbarn für BFS vormerken
        for neighbor in neighbors:
            if neighbor not in visited:
                # Als entdeckt markieren
                visited.add(neighbor)

                # Merken, woher wir gekommen sind
                parent[neighbor] = (x, y)

                # Hinten in die Queue einfügen
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
