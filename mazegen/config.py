import random
from dataclasses import dataclass
from typing import Tuple


@dataclass
class MazeConfig:
    """Holds configuration parameters for generating and rendering the maze."""

    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: int
    algorithm: str
    display: str
    no_dead_ends: bool

    def with_new_seed(self) -> "MazeConfig":
        """Generates a new configuration instance with a randomized seed value.

        Returns:
            A new MazeConfig object with a randomized seed integer.
        """
        return MazeConfig(
            width=self.width,
            height=self.height,
            entry=self.entry,
            exit=self.exit,
            output_file=self.output_file,
            perfect=self.perfect,
            seed=random.randint(0, 999999),
            algorithm=self.algorithm,
            display=self.display,
            no_dead_ends=self.no_dead_ends,
        )

    @classmethod
    def from_file(cls, filepath: str) -> "MazeConfig":
        """Parses a config text file to build and return a MazeConfig instance.

        Args:
            filepath: The path to the configuration text file.

        Returns:
            A fully populated MazeConfig object initialized from file values.
        """
        raw_config = {}
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    raw_config[key.strip().upper()] = val.strip()

        entry_x, entry_y = map(int, raw_config["ENTRY"].split(","))
        exit_x, exit_y = map(int, raw_config["EXIT"].split(","))

        return cls(
            width=int(raw_config["WIDTH"]),
            height=int(raw_config["HEIGHT"]),
            entry=(entry_x, entry_y),
            exit=(exit_x, exit_y),
            output_file=raw_config["OUTPUT_FILE"],
            perfect=raw_config["PERFECT"].lower() == "true",
            seed=int(raw_config["SEED"]),
            algorithm=raw_config["ALGORITHM"].lower(),
            display=raw_config["DISPLAY"].lower(),
            no_dead_ends=raw_config.get(
                "NO_DEAD_ENDS", "false"
            ).lower() == "true",
        )
