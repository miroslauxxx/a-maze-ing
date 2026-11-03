"""Configuration parser and validator for A-Maze-ing."""

import os
from typing import Any

MANDATORY_KEYS: tuple[str, ...] = (
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
)

ALL_KEYS: tuple[str, ...] = MANDATORY_KEYS + ("SEED",)


class ConfigError(ValueError):
    """Exception raised when configuration is invalid or missing."""

    pass


class Config:
    """Parser and container for maze configuration settings."""

    def __init__(self) -> None:
        """Initialize an empty configuration container."""
        self._params: dict[str, str] = {}
        self._width: int = 0
        self._height: int = 0
        self._entry: tuple[int, int] = (0, 0)
        self._exit: tuple[int, int] = (0, 0)
        self._output_file: str = ""
        self._perfect: bool = True
        self._seed: int | None = None

    @property
    def width(self) -> int:
        """Return the maze width."""
        return self._width

    @property
    def height(self) -> int:
        """Return the maze height."""
        return self._height

    @property
    def entry(self) -> tuple[int, int]:
        """Return the (x, y) coordinates for the entry."""
        return self._entry

    @property
    def exit(self) -> tuple[int, int]:
        """Return the (x, y) coordinates for the exit."""
        return self._exit

    @property
    def output_file(self) -> str:
        """Return the target output file path."""
        return self._output_file

    @property
    def perfect(self) -> bool:
        """Return True if the maze should be perfect (no loops)."""
        return self._perfect

    @property
    def seed(self) -> int | None:
        """Return the optional random generator seed."""
        return self._seed

    def _parse_bool(self, value: str) -> bool:
        """Parse a boolean value string.

        Args:
            value: String representation of boolean.

        Returns:
            Boolean value.

        Raises:
            ConfigError: If string is not a recognized boolean.
        """
        low = value.strip().lower()
        if low in ("true", "1", "yes", "y"):
            return True
        if low in ("false", "0", "no", "n"):
            return False
        raise ConfigError(f"Invalid boolean value for PERFECT: '{value}'")

    def _parse_coord(self, value: str, name: str) -> tuple[int, int]:
        """Parse coordinate string formatted as 'x,y'.

        Args:
            value: Coordinate string.
            name: Key name for error reporting.

        Returns:
            Tuple of (x, y) integers.

        Raises:
            ConfigError: If coordinates are improperly formatted.
        """
        parts = value.split(",")
        if len(parts) != 2:
            raise ConfigError(f"Invalid {name} coordinate format: '{value}' (expected 'x,y')")
        try:
            x = int(parts[0].strip())
            y = int(parts[1].strip())
            return (x, y)
        except ValueError as exc:
            raise ConfigError(f"Invalid integer in {name} coordinates: '{value}'") from exc

    def validate(self, filename: str) -> None:
        """Read and validate the configuration file.

        Args:
            filename: Path to the configuration file.

        Raises:
            ConfigError: If the file is missing or contains invalid settings.
        """
        if not os.path.exists(filename):
            raise ConfigError(f"Configuration file not found: '{filename}'")

        self._params = {}
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line_no, raw_line in enumerate(file, start=1):
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        raise ConfigError(
                            f"Syntax error on line {line_no} in '{filename}': missing '='"
                        )
                    key, val = line.split("=", 1)
                    clean_key = key.strip().upper()
                    clean_val = val.strip()
                    self._params[clean_key] = clean_val
        except OSError as exc:
            raise ConfigError(f"Failed to read configuration file '{filename}': {exc}") from exc

        # Check mandatory keys
        missing_keys = [k for k in MANDATORY_KEYS if k not in self._params]
        if missing_keys:
            raise ConfigError(
                f"Missing mandatory configuration key(s): {', '.join(missing_keys)}"
            )

        # Parse WIDTH and HEIGHT
        try:
            self._width = int(self._params["WIDTH"])
            self._height = int(self._params["HEIGHT"])
        except ValueError as exc:
            raise ConfigError(f"WIDTH and HEIGHT must be valid integers: {exc}") from exc

        if self._width < 3 or self._height < 3:
            raise ConfigError(
                f"Maze dimensions must be at least 3x3, got {self._width}x{self._height}"
            )

        # Parse ENTRY and EXIT
        self._entry = self._parse_coord(self._params["ENTRY"], "ENTRY")
        self._exit = self._parse_coord(self._params["EXIT"], "EXIT")

        ex, ey = self._entry
        if not (0 <= ex < self._width and 0 <= ey < self._height):
            raise ConfigError(
                f"ENTRY {self._entry} is out of bounds for maze of size "
                f"{self._width}x{self._height}"
            )

        qx, qy = self._exit
        if not (0 <= qx < self._width and 0 <= qy < self._height):
            raise ConfigError(
                f"EXIT {self._exit} is out of bounds for maze of size "
                f"{self._width}x{self._height}"
            )

        if self._entry == self._exit:
            raise ConfigError(f"ENTRY and EXIT cannot be identical: {self._entry}")

        # Parse OUTPUT_FILE
        self._output_file = self._params["OUTPUT_FILE"]
        if not self._output_file:
            raise ConfigError("OUTPUT_FILE must not be empty")

        # Parse PERFECT
        self._perfect = self._parse_bool(self._params["PERFECT"])

        # Parse optional SEED
        if "SEED" in self._params and self._params["SEED"]:
            try:
                self._seed = int(self._params["SEED"])
            except ValueError as exc:
                raise ConfigError(f"Invalid integer for SEED: '{self._params['SEED']}'") from exc
        else:
            self._seed = None

    def as_dict(self) -> dict[str, Any]:
        """Return the configuration parameters as a dictionary."""
        return {
            "width": self._width,
            "height": self._height,
            "entry": self._entry,
            "exit": self._exit,
            "output_file": self._output_file,
            "perfect": self._perfect,
            "seed": self._seed,
        }


def parse_config(filename: str) -> Config:
    """Load, validate, and return a Config object for a file.

    Args:
        filename: Path to the configuration file.

    Returns:
        Configured and validated Config instance.
    """
    config = Config()
    config.validate(filename)
    return config
