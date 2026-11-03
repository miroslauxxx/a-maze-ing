"""Output file writer module for the maze generator."""

from typing import Sequence


def format_maze_output(
    maze: Sequence[Sequence[int]],
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
    shortest_path_directions: str,
) -> str:
    """Format the maze and solution into the project output string format.

    Args:
        maze: 2D grid of wall integers (0-15).
        entry: (x, y) coordinates of the maze entry.
        exit_pos: (x, y) coordinates of the maze exit.
        shortest_path_directions: String of N, E, S, W characters representing the solution.

    Returns:
        The formatted string representing the output file content.
    """
    lines: list[str] = []
    for row in maze:
        lines.append("".join(f"{cell:X}" for cell in row).lower())
    lines.append("")
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit_pos[0]},{exit_pos[1]}")
    lines.append(shortest_path_directions)
    return "\n".join(lines) + "\n"


def write_maze_file(
    filename: str,
    maze: Sequence[Sequence[int]],
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
    shortest_path_directions: str,
) -> None:
    """Write the maze and its solution to a specified file.

    Args:
        filename: Path to the target output file.
        maze: 2D grid of wall integers (0-15).
        entry: (x, y) coordinates of the maze entry.
        exit_pos: (x, y) coordinates of the maze exit.
        shortest_path_directions: String of N, E, S, W characters.
    """
    content = format_maze_output(maze, entry, exit_pos, shortest_path_directions)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
