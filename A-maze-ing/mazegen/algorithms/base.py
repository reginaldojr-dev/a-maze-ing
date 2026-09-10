from abc import ABC, abstractmethod
import random
from typing import Generator, Tuple
from mazegen.maze import Maze


class MazeAlgorithm(ABC):
	@abstractmethod
	def generate(
		self, maze: Maze, rng: random.Random, start_pos: Tuple[int, int]
	) -> Generator[Maze, None, None]:
		pass