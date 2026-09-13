from abc import ABC, abstractmethod
import random
from typing import Generator, Tuple
from mazegen.maze import Maze


class MazeAlgorithm(ABC):
    """Abstract base class defin the interface for maze generat algorithms."""

    @abstractmethod
    def generate(
        self, maze: Maze, rng: random.Random, start_pos: Tuple[int, int]
    ) -> Generator[Maze, None, None]:
        """Generates the maze layout by carving passages through the grid.

        Args:
            maze: The Maze instance to modify.
            rng: The random number generator instance.
            start_pos: The starting coordinate tuple (x, y).

        Returns:
            A generator yielding the Maze instance during generation steps.
        """
        pass
