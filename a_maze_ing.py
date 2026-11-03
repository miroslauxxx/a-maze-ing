#!/usr/bin/env python3
import argparse
import os
import random
import sys
from dataclasses import dataclass
from typing import Sequence

from mazegen.config import Config, ConfigError, parse_config
from mazegen.generator import MazeGenerationError, MazeGenerator
from mazegen.solver import solve_maze
from mazegen.writer import write_maze_file


@dataclass(frozen=True)
class ColorTheme:
    """ANSI color scheme definition for TUI rendering."""

    name: str
    wall: str
    path: str
    entry: str
    exit_marker: str
    pattern_42: str
    reset: str = "\033[0m"


THEMES: list[ColorTheme] = [
    ColorTheme(
        name="Cyan Neon",
        wall="\033[1;36m",
        path="\033[1;33m",
        entry="\033[1;32m",
        exit_marker="\033[1;31m",
        pattern_42="\033[1;35m",
    ),
    ColorTheme(
        name="Matrix Green",
        wall="\033[1;32m",
        path="\033[1;97m",
        entry="\033[1;36m",
        exit_marker="\033[1;33m",
        pattern_42="\033[32m",
    ),
    ColorTheme(
        name="Cyberpunk Magenta",
        wall="\033[1;35m",
        path="\033[1;36m",
        entry="\033[1;32m",
        exit_marker="\033[1;91m",
        pattern_42="\033[1;33m",
    ),
    ColorTheme(
        name="Solar Amber",
        wall="\033[1;33m",
        path="\033[1;31m",
        entry="\033[1;32m",
        exit_marker="\033[1;35m",
        pattern_42="\033[1;36m",
    ),
    ColorTheme(
        name="Classic Monochrome",
        wall="\033[1;37m",
        path="\033[1;93m",
        entry="\033[1;92m",
        exit_marker="\033[1;91m",
        pattern_42="\033[2;37m",
    ),
]


def get_box_char(up: bool, right: bool, down: bool, left: bool) -> str:
    """Return the appropriate Unicode box-drawing character for a vertex.

    Args:
        up: Whether a wall goes upwards.
        right: Whether a wall goes to the right.
        down: Whether a wall goes downwards.
        left: Whether a wall goes to the left.

    Returns:
        Unicode box character string.
    """
    table = {
        (False, False, False, False): " ",
        (False, True, False, True): "─",
        (True, False, True, False): "│",
        (False, True, True, False): "┌",
        (False, False, True, True): "┐",
        (True, True, False, False): "└",
        (True, False, False, True): "┘",
        (False, True, True, True): "┬",
        (True, True, False, True): "┴",
        (True, True, True, False): "├",
        (True, False, True, True): "┤",
        (True, True, True, True): "┼",
        (True, False, False, False): "│",
        (False, True, False, False): "─",
        (False, False, True, False): "│",
        (False, False, False, True): "─",
    }
    return table.get((up, right, down, left), " ")


def render_maze(
    generator: MazeGenerator,
    path: Sequence[tuple[int, int]],
    show_path: bool,
    theme: ColorTheme,
) -> str:
    """Render the maze into a string formatted with Unicode box characters and ANSI colors.

    Args:
        generator: MazeGenerator instance.
        path: Sequence of (x, y) coordinates for the solution path.
        show_path: Whether the path should be visible.
        theme: Active ColorTheme.

    Returns:
        Rendered string suitable for terminal display.
    """
    maze = generator.maze
    w, h = generator.width, generator.height
    path_set = set(path) if show_path else set()

    lines: list[str] = []
    w_col = theme.wall
    reset = theme.reset

    for r in range(h + 1):
        # Wall and vertex line
        wall_parts: list[str] = []
        for c in range(w + 1):
            up = False
            if r > 0:
                if c == 0 or c == w:
                    up = True
                elif 0 < c < w:
                    up = bool(maze[r - 1][c - 1] & 2)  # EAST wall

            down = False
            if r < h:
                if c == 0 or c == w:
                    down = True
                elif 0 < c < w:
                    down = bool(maze[r][c - 1] & 2)  # EAST wall

            left = False
            if c > 0:
                if r == 0 or r == h:
                    left = True
                elif 0 < r < h:
                    left = bool(maze[r - 1][c - 1] & 4)  # SOUTH wall

            right = False
            if c < w:
                if r == 0 or r == h:
                    right = True
                elif 0 < r < h:
                    right = bool(maze[r - 1][c] & 4)  # SOUTH wall

            char = get_box_char(up, right, down, left)
            wall_parts.append(f"{w_col}{char}{reset}")

            if c < w:
                segment = "───" if right else "   "
                wall_parts.append(f"{w_col}{segment}{reset}")

        lines.append("".join(wall_parts))

        # Cell interior line
        if r < h:
            cell_parts: list[str] = []
            for c in range(w):
                v_wall = bool(maze[r][c] & 8) if c > 0 else True  # WEST wall
                v_char = "│" if v_wall else " "
                cell_parts.append(f"{w_col}{v_char}{reset}")

                pos = (c, r)
                if pos == generator.entry:
                    cell_parts.append(f"{theme.entry} S {reset}")
                elif pos == generator.exit:
                    cell_parts.append(f"{theme.exit_marker} E {reset}")
                elif pos in generator.blocked:
                    cell_parts.append(f"{theme.pattern_42}███{reset}")
                elif pos in path_set:
                    cell_parts.append(f"{theme.path} · {reset}")
                else:
                    cell_parts.append("   ")

            # Final right boundary
            cell_parts.append(f"{w_col}│{reset}")
            lines.append("".join(cell_parts))

    return "\n".join(lines)


class MazeApp:
    """Interactive TUI controller application for A-Maze-ing."""

    def __init__(self, config: Config, debug: bool = False) -> None:
        """Initialize the application with parsed configuration.

        Args:
            config: Validated Config instance.
            debug: Whether to print diagnostic debugging output.
        """
        self.config: Config = config
        self.debug: bool = debug
        self.theme_idx: int = 0
        self.show_path: bool = True
        self.seed: int | None = config.seed

        self.generator: MazeGenerator = self._build_generator(self.seed)
        self.path: list[tuple[int, int]] = []
        self.directions: str = ""
        self._update_maze()

    def _build_generator(self, seed: int | None) -> MazeGenerator:
        """Instantiate a new MazeGenerator using current config and given seed."""
        return MazeGenerator(
            width=self.config.width,
            height=self.config.height,
            perfect=self.config.perfect,
            seed=seed,
            entry=self.config.entry,
            exit=self.config.exit,
        )

    def _update_maze(self) -> None:
        """Generate maze, calculate solution path, and write output file."""
        self.generator.generate_maze()
        self.path, self.directions = solve_maze(
            self.generator.maze,
            self.generator.width,
            self.generator.height,
            self.generator.entry,
            self.generator.exit,
        )
        try:
            write_maze_file(
                self.config.output_file,
                self.generator.maze,
                self.generator.entry,
                self.generator.exit,
                self.directions,
            )
        except OSError as err:
            print(f"Warning: Could not write output file '{self.config.output_file}': {err}")

    def regenerate(self) -> None:
        """Create a fresh maze layout with a new random seed."""
        self.seed = random.randint(1, 999999)
        self.generator = self._build_generator(self.seed)
        self._update_maze()

    def toggle_path(self) -> None:
        """Toggle solution path visibility."""
        self.show_path = not self.show_path

    def rotate_colors(self) -> None:
        """Cycle to the next wall color theme."""
        self.theme_idx = (self.theme_idx + 1) % len(THEMES)

    @property
    def current_theme(self) -> ColorTheme:
        """Get currently active color theme."""
        return THEMES[self.theme_idx]

    def render_screen(self) -> None:
        """Display clear screen, header, maze grid, and menu."""
        theme = self.current_theme
        rendered = render_maze(self.generator, self.path, self.show_path, theme)

        # Clear screen for interactive display
        if sys.stdout.isatty():
            sys.stdout.write("\033[H\033[2J")

        mode_str = "Perfect (Lab Tree)" if self.config.perfect else "Imperfect (Pac-Man Board)"
        path_status = "VISIBLE" if self.show_path else "HIDDEN"

        print("=" * 60)
        print("          ★ A-Maze-ing - 42 Crocodile ★")
        print("=" * 60)
        print(f" Dimensions: {self.config.width}x{self.config.height}  |  Mode: {mode_str}")
        print(f" Seed: {self.seed}  |  Theme: {theme.name}  |  Path: {path_status}")
        print(f" Entry: {self.config.entry}  |  Exit: {self.config.exit}")
        print(f" Shortest Path Steps: {len(self.path)}")
        print(f" Output File: {self.config.output_file}")
        if self.debug:
            print(f" [Debug] Wall Coherence: {self.generator.check_wall_coherence()}")
            print(f" [Debug] Connectivity: {self.generator.check_connectivity()}")
            print(f" [Debug] Borders: {self.generator.check_borders()}")
            if self.config.perfect:
                print(f" [Debug] Loopless: {self.generator.check_no_loops()}")
            print(f" [Debug] Dead Ends: {self.generator.count_dead_ends()}")
        print("-" * 60)
        print(rendered)
        print("=" * 60)
        print(" [1] Re-generate a new maze")
        print(" [2] Show/Hide the shortest path")
        print(" [3] Change / Rotate wall colours")
        print(" [4] Quit")
        print("=" * 60)

    def run_interactive(self) -> None:
        """Main interactive loop."""
        while True:
            self.render_screen()
            try:
                choice = input(" Select option (1-4): ").strip()
                if choice == "1":
                    self.regenerate()
                elif choice == "2":
                    self.toggle_path()
                elif choice == "3":
                    self.rotate_colors()
                elif choice == "4" or choice.lower() in ("q", "quit", "exit"):
                    print("\nExiting A-Maze-ing. Goodbye!")
                    break
                elif choice == "":
                    self.regenerate()
                else:
                    input(" Invalid option. Press Enter to continue...")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting A-Maze-ing. Goodbye!")
                break


def main() -> int:
    """Application entry point.

    Returns:
        Process exit code (0 for success, non-zero for error).
    """
    parser = argparse.ArgumentParser(
        description="A-Maze-ing - 42 Terminal Maze Generator & Solver"
    )
    parser.add_argument(
        "config",
        nargs="?",
        default=None,
        help="Path to configuration file (defaults to config.txt or config)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable diagnostic debugging checks and outputs",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without interactive menu, generate maze, write file, and exit",
    )

    args = parser.parse_args()

    # Determine configuration file path
    config_path = args.config
    if not config_path:
        if os.path.exists("config.txt"):
            config_path = "config.txt"
        elif os.path.exists("config"):
            config_path = "config"
        else:
            print("Error: No configuration file found (expected 'config.txt' or 'config').")
            return 1

    try:
        config = parse_config(config_path)
    except ConfigError as err:
        print(f"Configuration Error in '{config_path}': {err}")
        return 1

    try:
        app = MazeApp(config, debug=args.debug)
    except MazeGenerationError as err:
        print(f"Maze Generation Error: {err}")
        return 1

    if args.non_interactive:
        app.render_screen()
        print(f"Maze successfully generated and written to '{config.output_file}'.")
        return 0

    app.run_interactive()
    return 0


if __name__ == "__main__":
    sys.exit(main())
