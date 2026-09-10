import random
from typing import Dict, Type, List
from mazegen.config import MazeConfig
from mazegen.maze import Maze
from mazegen.solver import solve_bfs
from mazegen.exceptions import GenerationError, PathNotFoundError
from mazegen.algorithms.base import MazeAlgorithm

ALGORITHMS: Dict[str, Type[MazeAlgorithm]] = {}


def register_algorithm(name: str, algo_cls: Type[MazeAlgorithm]) -> None:
    """Permite registrar dinamicamente algoritmos para extensibilidade."""
    ALGORITHMS[name.lower()] = algo_cls


class MazeGenerator:
    def __init__(self, config: MazeConfig):
        self.config = config
        self.rng = random.Random(config.seed)

    def create_maze(self, algorithm: MazeAlgorithm) -> Maze:
        maze = Maze(self.config.width, self.config.height, self.config.entry, self.config.exit)
        maze.apply_42_pattern()

        gen = algorithm.generate(maze, self.rng, self.config.entry)
        for _ in gen:
            pass

        if not self.config.perfect:
            maze.ensure_pacman_intersections()
            maze.add_random_loops(self.rng, extra_passages=max(2, (maze.width * maze.height) // 20))

        if self.config.no_dead_ends:
            maze.braid(self.rng)

        return maze

    def get_solution(self, maze: Maze) -> List[str]:
        path = solve_bfs(maze, self.config.entry, self.config.exit)
        if not path:
            raise PathNotFoundError("Impossível alcançar EXIT a partir de ENTRY.")
        return path