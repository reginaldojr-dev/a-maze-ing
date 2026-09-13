import random
from typing import Generator, Tuple

from mazegen.algorithms.base import MazeAlgorithm
from mazegen.maze import Maze


class RecursiveBacktracker(MazeAlgorithm):
    """Generates a maze using the random recursive backtracker algorithm."""

    def generate(
        self,
        maze: Maze,
        rng: random.Random,
        start_pos: Tuple[int, int],
    ) -> Generator[Maze, None, None]:
        """Carves pass through the maze utiliz a depth-first search approach.

        Args:
            maze: The Maze instance to carve passages into.
            rng: The random number generator instance.
            start_pos: The starting coordinate tuple (x, y) for generation.

        Returns:
            A generator yielding the Maze instance at each carving step.
        """
        stack = [start_pos]
        visited = {start_pos}

        while stack:
            current = stack[-1]
            current_x, current_y = current

            neighbors = []

            for direction, (nx, ny) in maze.get_neighbor_coords(
                current_x, current_y
            ):
                if (
                    (nx, ny) not in visited
                    and not maze.cell_at(nx, ny).is_blocked
                ):
                    neighbors.append((direction, (nx, ny)))

            if not neighbors:
                stack.pop()
            else:
                direction, (nx, ny) = rng.choice(neighbors)
                maze.open_passage(current_x, current_y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
            yield maze
