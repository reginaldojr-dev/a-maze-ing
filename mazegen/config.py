from dataclasses import dataclass
from typing import Optional, Tuple
import os
from mazegen.exceptions import ConfigError


@dataclass(frozen=True)
class MazeConfig:
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None
    algorithm: str = "backtracker"
    display: str = "ascii"
    no_dead_ends: bool = False

    @classmethod
    def from_file(cls, filepath: str) -> "MazeConfig":
        if not os.path.exists(filepath):
            raise ConfigError(f"File config '{filepath}' no_search.")
        raw_config = {}
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        raise ConfigError(f"Error line {line_num}: '{line}'")
                    key, val = line.split("=", 1)
                    raw_config[key.strip().upper()] = val.strip()
        except OSError as e:
            raise ConfigError(f"Error I/O read file: {e}")
        return cls._parse_dict(raw_config)

    @classmethod
    def _parse_dict(cls, raw: dict) -> "MazeConfig":
        required = {
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
            "PERFECT",
        }
        missing = required - raw.keys()
        if missing:
            raise ConfigError(f"Key missing: {', '.join(missing)}")
        try:
            width = int(raw["WIDTH"])
            height = int(raw["HEIGHT"])
            if width <= 0 or height <= 0:
                raise ConfigError(f"Dimension error: {width}x{height}")
            entry = cls._parse_coords(raw["ENTRY"], "ENTRY")
            exit_c = cls._parse_coords(raw["EXIT"], "EXIT")
            if not (0 <= entry[0] < width and 0 <= entry[1] < height):
                raise ConfigError(f"ENTRY {entry} Out of bounds.")
            if not (0 <= exit_c[0] < width and 0 <= exit_c[1] < height):
                raise ConfigError(f"EXIT {exit_c} Out of bounds.")
            if entry == exit_c:
                raise ConfigError("ENTRY e EXIT dont identic.")
            perfect = raw["PERFECT"].lower() in ("true", "1", "yes")
            seed = int(raw["SEED"]) if "SEED" in raw else None
            algorithm = raw.get("ALGORITHM", "backtracker").lower()
            display = raw.get("DISPLAY", "ascii").lower()
            no_dead_ends = (
                raw.get("NO_DEAD_ENDS", "false").lower()
                in ("true", "1", "yes")
            )
            return cls(
                width=width,
                height=height,
                entry=entry,
                exit=exit_c,
                output_file=raw["OUTPUT_FILE"],
                perfect=perfect,
                seed=seed,
                algorithm=algorithm,
                display=display,
                no_dead_ends=no_dead_ends
            )
        except ValueError as e:
            raise ConfigError(f"Error parsing number: {e}")

    @staticmethod
    def _parse_coords(coord_str: str, name: str) -> Tuple[int, int]:
        parts = coord_str.split(",")
        if len(parts) != 2:
            raise ConfigError(f"Format invalible {name}: '{coord_str}'")
        return int(parts[0].strip()), int(parts[1].strip())
