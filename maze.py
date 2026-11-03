"""Maze generation module providing the MazeGenerator class."""

import sys

from mazegen.generator import (
    ALL_WALLS,
    EAST,
    NORTH,
    SOUTH,
    WEST,
    MazeGenerationError,
    MazeGenerator,
)

__all__ = [
    "MazeGenerator",
    "MazeGenerationError",
    "NORTH",
    "EAST",
    "SOUTH",
    "WEST",
    "ALL_WALLS",
]


def _demo() -> None:
    """Run verification and demonstration of MazeGenerator."""
    seed = 42
    entry = (0, 0)
    exit_pos = (9, 9)

    generator = MazeGenerator(10, 10, True, seed, entry, exit_pos)

    if not generator.check_entry_exit():
        print("Error: Invalid entry or exit.")
        sys.exit(1)

    print("Perfect:", generator.perfect)
    print("Entry/Exit valid:", generator.check_entry_exit())

    maze = generator.generate_maze()

    print("No loops:", generator.check_no_loops())
    print("Wall coherence:", generator.check_wall_coherence())
    print("Connected:", generator.check_connectivity())
    generator.check_borders()

    for start_y in range(generator.height - 2):
        for start_x in range(generator.width - 2):
            if generator.is_open_3x3(start_x, start_y):
                print("OPEN 3x3 FOUND:", start_x, start_y)

    print("Dead ends:", generator.count_dead_ends())

    for row in maze:
        print(row)


if __name__ == "__main__":
    _demo()
