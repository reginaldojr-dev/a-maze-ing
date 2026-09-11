from typing import Generator, Tuple
import random

from mazegen.walls import Wall
from mazegen.maze import Maze
from mazegen.algorithms.base import MazeAlgorithm


class DisjointSet:
    def __init__(
        self,
        cells: list[Tuple[int, int]]
    ) -> None:
        self.parent: dict[
            Tuple[int, int],
            Tuple[int, int]
        ] = {
            cell: cell for cell in cells
        }

    def find(
        self,
        cell: Tuple[int, int]
    ) -> Tuple[int, int]:
        if self.parent[cell] != cell:
            self.parent[cell] = self.find(self.parent[cell])
        return self.parent[cell]

    def union(
        self,
        first: Tuple[int, int],
        second: Tuple[int, int]
    ) -> None:
        root_first = self.find(first)
        root_second = self.find(second)

        if root_first != root_second:
            self.parent[root_second] = root_first


class KruskalAlgorithm(MazeAlgorithm):
    def generate(
        self,
        maze: Maze,
        rng: random.Random,
        start_pos: Tuple[int, int]
    ) -> Generator[Maze, None, None]:
        _ = start_pos

        cells = [
            (x, y)
            for y in range(maze.height)
            for x in range(maze.width)
            if not maze.cell_at(x, y).is_blocked
        ]

        sets = DisjointSet(cells)

        edges: list[
            tuple[
                Tuple[int, int],
                Tuple[int, int],
                Wall
            ]
        ] = []

        for x, y in cells:
            for direction, (nx, ny) in maze.get_neighbor_coords(x, y):
                if direction not in (Wall.EAST, Wall.SOUTH):
                    continue

                if maze.cell_at(nx, ny).is_blocked:
                    continue

                edges.append(((x, y), (nx, ny), direction))

        rng.shuffle(edges)

        for first, second, direction in edges:
            if sets.find(first) == sets.find(second):
                continue

            x, y = first

            maze.open_passage(x, y, direction)
            sets.union(first, second)

            yield maze
