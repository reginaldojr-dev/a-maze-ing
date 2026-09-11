import random
from typing import Generator, Tuple
from mazegen.algorithms.base import MazeAlgorithm
from mazegen.maze import Maze


class PrimAlgorithm(MazeAlgorithm):
    def generate(
        self,
        maze: Maze,
        rng: random.Random,
        start_pos: Tuple[int, int],
    ) -> Generator[Maze, None, None]:
        visited = {start_pos}
        cx, cy = start_pos
        frontier = [
            (direction, (cx, cy), (nx, ny))
            for direction, (nx, ny) in maze.get_neighbor_coords(cx, cy)
            if not maze.cell_at(nx, ny).is_blocked
        ]
        while frontier:
            index = rng.randrange(len(frontier))
            direction, (cx, cy), (nx, ny) = frontier.pop(index)
            if (nx, ny) in visited:
                continue

            maze.open_passage(cx, cy, direction)
            visited.add((nx, ny))

            frontier.extend([
                (new_direction, (nx, ny), (new_x, new_y))
                for new_direction, (new_x, new_y)
                in maze.get_neighbor_coords(nx, ny)
                if (
                    (new_x, new_y) not in visited
                    and not maze.cell_at(new_x, new_y).is_blocked
                )
            ])
            yield maze
