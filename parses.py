"""Configuration file parser module for A-Maze-ing."""

import sys
from mazegen.config import Config, ConfigError, parse_config

spaces: list[str] = [" ", "\t", "\n"]
settings: list[str] = [
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
    "SEED",
]

__all__ = ["Config", "ConfigError", "parse_config", "spaces", "settings"]


def _demo() -> None:
    """Run demonstration/test of Config parser."""
    conf_file = sys.argv[1] if len(sys.argv) > 1 else "config"
    config = Config()
    try:
        config.validate(conf_file)
        print(
            config.width,
            config.height,
            config.entry,
            config.exit,
            config.output_file,
            config.perfect,
            config.seed,
        )
    except ConfigError as err:
        print(f"Validation error: {err}")


if __name__ == "__main__":
    _demo()
