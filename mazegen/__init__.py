"""mazegen - Reusable maze generator and solver module."""

from mazegen.config import Config, ConfigError, parse_config
from mazegen.generator import (
    ALL_WALLS,
    EAST,
    NORTH,
    SOUTH,
    WEST,
    MazeGenerationError,
    MazeGenerator,
)
from mazegen.solver import solve, solve_maze
from mazegen.writer import format_maze_output, write_maze_file

__version__ = "1.0.0"

__all__ = [
    "MazeGenerator",
    "MazeGenerationError",
    "NORTH",
    "EAST",
    "SOUTH",
    "WEST",
    "ALL_WALLS",
    "solve",
    "solve_maze",
    "Config",
    "ConfigError",
    "parse_config",
    "format_maze_output",
    "write_maze_file",
]
