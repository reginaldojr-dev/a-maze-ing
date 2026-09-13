import random
from typing import Dict, Generator, List, Tuple

from mazegen.algorithms.base import MazeAlgorithm
from mazegen.maze import Maze
from mazegen.walls import Wall


class DisjointSet:
    """Manages disjoint sets for Kruskal's maze generation algorithm."""

    def __init__(
        self,
        cells: List[Tuple[int, int]]
    ) -> None:
        """Initializes the disjoint sets with each cell as its own parent.

        Args:
            cells: A list of coordinate tuples representing valid cells.

        Returns:
            None
        """
        self.parent: Dict[
            Tuple[int, int],
            Tuple[int, int]
        ] = {
            cell: cell for cell in cells
        }

    def find(
        self,
        cell: Tuple[int, int]
    ) -> Tuple[int, int]:
        """Finds the root representative of a given cell with path compression.

        Args:
            cell: The coordinate tuple of the cell to locate.

        Returns:
            The coordinate tuple of the set's root representative.
        """
        if self.parent[cell] != cell:
            self.parent[cell] = self.find(self.parent[cell])
        return self.parent[cell]

    def union(
        self,
        first: Tuple[int, int],
        second: Tuple[int, int]
    ) -> None:
        """Merges the sets containing the two specified cells.

        Args:
            first: The coordinate tuple of the first cell.
            second: The coordinate tuple of the second cell.

        Returns:
            None
        """
        root_first = self.find(first)
        root_second = self.find(second)

        if root_first != root_second:
            self.parent[root_second] = root_first


class KruskalAlgorithm(MazeAlgorithm):
    """Generates a maze using random Kruskal's algorithm with disjoint sets."""

    def generate(
        self,
        maze: Maze,
        rng: random.Random,
        start_pos: Tuple[int, int]
    ) -> Generator[Maze, None, None]:
        """Generates passages through randomized edge processing.

        Args:
            maze: The Maze instance to carve passages into.
            rng: The random number generator instance.
            start_pos: The starting coordinate tuple (unused in Kruskal).

        Returns:
            A generator yielding the Maze instance after each step.
        """
        _ = start_pos

        cells = [
            (x, y)
            for y in range(maze.height)
            for x in range(maze.width)
            if not maze.cell_at(x, y).is_blocked
        ]

        sets = DisjointSet(cells)

        edges: List[
            Tuple[
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
        yield maze
