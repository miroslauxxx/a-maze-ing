"""Comprehensive test suite for mazegen, config, solver, and CLI."""

import os
import tempfile
import pytest

from mazegen.config import ConfigError, parse_config
from mazegen.generator import MazeGenerationError, MazeGenerator
from mazegen.solver import solve, solve_maze
from mazegen.writer import format_maze_output, write_maze_file


def test_generator_perfect_reproducibility() -> None:
    """Test that the same seed produces identical mazes."""
    gen1 = MazeGenerator(21, 15, perfect=True, seed=1234, entry=(0, 0), exit=(20, 14))
    m1 = gen1.generate_maze()

    gen2 = MazeGenerator(21, 15, perfect=True, seed=1234, entry=(0, 0), exit=(20, 14))
    m2 = gen2.generate_maze()

    assert m1 == m2
    assert gen1.get_solution_directions() == gen2.get_solution_directions()


def test_generator_perfect_properties() -> None:
    """Test properties of a perfect maze (tree structure, no loops)."""
    gen = MazeGenerator(19, 13, perfect=True, seed=42, entry=(0, 0), exit=(18, 12))
    gen.generate_maze()

    assert gen.check_wall_coherence() is True
    assert gen.check_borders() is True
    assert gen.check_connectivity() is True
    assert gen.check_no_loops() is True


def test_generator_imperfect_pacman_properties() -> None:
    """Test properties of an imperfect (Pac-Man style) maze."""
    gen = MazeGenerator(25, 17, perfect=False, seed=999, entry=(0, 0), exit=(24, 16))
    gen.generate_maze()

    assert gen.check_wall_coherence() is True
    assert gen.check_borders() is True
    assert gen.check_connectivity() is True
    # In imperfect mode, loops are added, so check_no_loops should be False
    assert gen.check_no_loops() is False

    # Verify no open 3x3 areas exist anywhere
    for y in range(gen.height - 2):
        for x in range(gen.width - 2):
            assert gen.is_open_3x3(x, y) is False


def test_42_pattern_presence_and_small_maze() -> None:
    """Test 42 pattern is present in large mazes and handled gracefully in small mazes."""
    # Large maze
    gen_large = MazeGenerator(15, 11, perfect=True, seed=1)
    assert len(gen_large.blocked) > 0

    # Every cell in blocked must have ALL_WALLS (15)
    gen_large.generate_maze()
    for bx, by in gen_large.blocked:
        assert gen_large.maze[by][bx] == 15

    # Small maze (< 9x7)
    gen_small = MazeGenerator(8, 6, perfect=True, seed=1)
    assert len(gen_small.blocked) == 0
    assert len(gen_small.generate_maze()) == 6
    assert gen_small.check_connectivity() is True
    assert gen_small.check_wall_coherence() is True


def test_solver_shortest_path() -> None:
    """Test that BFS solver finds a valid, contiguous path following open walls."""
    gen = MazeGenerator(17, 13, perfect=True, seed=77, entry=(0, 0), exit=(16, 12))
    maze = gen.generate_maze()

    path, directions = solve_maze(maze, gen.width, gen.height, gen.entry, gen.exit)
    assert len(path) > 0
    assert path[0] == gen.entry
    assert path[-1] == gen.exit
    assert len(directions) == len(path) - 1

    # Verify path steps correspond exactly to directions
    for i in range(len(directions)):
        curr_x, curr_y = path[i]
        next_x, next_y = path[i + 1]
        move = directions[i]
        if move == "N":
            assert (next_x, next_y) == (curr_x, curr_y - 1)
            assert not (maze[curr_y][curr_x] & 1)
        elif move == "E":
            assert (next_x, next_y) == (curr_x + 1, curr_y)
            assert not (maze[curr_y][curr_x] & 2)
        elif move == "S":
            assert (next_x, next_y) == (curr_x, curr_y + 1)
            assert not (maze[curr_y][curr_x] & 4)
        elif move == "W":
            assert (next_x, next_y) == (curr_x - 1, curr_y)
            assert not (maze[curr_y][curr_x] & 8)

    # Test solve helper
    helper_path = solve(gen)
    assert helper_path == path


def test_config_parser_valid() -> None:
    """Test parsing a valid config file."""
    content = """# Comment line
WIDTH = 30
HEIGHT = 20
ENTRY = 1,1
EXIT = 28,18
OUTPUT_FILE = test_out.txt
PERFECT = False
SEED = 54321
"""
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(content)
        temp_name = f.name

    try:
        cfg = parse_config(temp_name)
        assert cfg.width == 30
        assert cfg.height == 20
        assert cfg.entry == (1, 1)
        assert cfg.exit == (28, 18)
        assert cfg.output_file == "test_out.txt"
        assert cfg.perfect is False
        assert cfg.seed == 54321
    finally:
        os.remove(temp_name)


def test_config_parser_errors() -> None:
    """Test error handling in configuration parser."""
    # Missing file
    with pytest.raises(ConfigError):
        parse_config("non_existent_file_xyz.txt")

    # Missing mandatory key
    bad_content = "WIDTH = 10\nHEIGHT = 10\n"
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(bad_content)
        bad_name = f.name

    try:
        with pytest.raises(ConfigError):
            parse_config(bad_name)
    finally:
        os.remove(bad_name)

    # Out of bounds coordinates
    oob_content = """WIDTH = 10
HEIGHT = 10
ENTRY = 0,0
EXIT = 15,15
OUTPUT_FILE = out.txt
PERFECT = True
"""
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(oob_content)
        oob_name = f.name

    try:
        with pytest.raises(ConfigError):
            parse_config(oob_name)
    finally:
        os.remove(oob_name)


def test_output_file_writer() -> None:
    """Test formatting and writing the output file."""
    maze = [[11, 3], [14, 6]]
    entry = (0, 0)
    exit_pos = (1, 1)
    directions = "ES"

    formatted = format_maze_output(maze, entry, exit_pos, directions)
    expected = "b3\ne6\n\n0,0\n1,1\nES\n"
    assert formatted == expected

    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        temp_path = f.name

    try:
        write_maze_file(temp_path, maze, entry, exit_pos, directions)
        with open(temp_path, "r", encoding="utf-8") as f:
            read_back = f.read()
        assert read_back == expected
    finally:
        os.remove(temp_path)


def test_entry_exit_in_blocked_pattern() -> None:
    """Test graceful handling when entry or exit lands on the blocked 42 pattern."""
    # For a 15x11 maze:
    # offset_x = (15 - 7) // 2 = 4
    # offset_y = (11 - 5) // 2 = 3
    # Pattern cell (0, 0) centered is at (4, 3)
    blocked_coord = (4, 3)

    # Entry on blocked cell
    with pytest.raises(MazeGenerationError) as exc_info:
        MazeGenerator(15, 11, perfect=True, entry=blocked_coord, exit=(14, 10))
    assert "ENTRY" in str(exc_info.value)
    assert "blocked" in str(exc_info.value)

    # Exit on blocked cell
    with pytest.raises(MazeGenerationError) as exc_info:
        MazeGenerator(15, 11, perfect=True, entry=(0, 0), exit=blocked_coord)
    assert "EXIT" in str(exc_info.value)
    assert "blocked" in str(exc_info.value)
