from typing import Generator, Tuple
import random

from mazegen.maze import Maze
from mazegen.algorithms.base import MazeAlgorithm


class RecursiveBacktracker(MazeAlgorithm):
    def generate(
            self,
            maze: Maze,
            rng: random.Random,
            start_pos: Tuple[int, int]
            ) -> Generator[Maze, None, None]:
        stack = [start_pos]
        visited = {start_pos}

        while stack:
            current = stack[-1]
            current_x, current_y = current

            neighbors = []

            for direction, (nx, ny) in maze.get_neighbor_coords(
                    current_x, current_y):
                if (nx, ny) not in visited and not maze.cell_at(
                        nx, ny).is_blocked:
                    neighbors.append((direction, (nx, ny)))

            if not neighbors:
                stack.pop()
            else:
                direction, (nx, ny) = rng.choice(neighbors)
                maze.open_passage(current_x, current_y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
            yield maze
