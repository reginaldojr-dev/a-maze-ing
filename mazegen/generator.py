import random
import time
from typing import Dict, List, Type
from mazegen.algorithms.base import MazeAlgorithm
from mazegen.config import MazeConfig
from mazegen.exceptions import PathNotFoundError
from mazegen.maze import Maze
from mazegen.solver import solve_bfs
from renderers.base import BaseRenderer

ALGORITHMS: Dict[str, Type[MazeAlgorithm]] = {}


def register_algorithm(name: str, algo_cls: Type[MazeAlgorithm]) -> None:
    """Registers a new maze generation algorithm class in the global registry.

    Args:
        name: The name identifier for the algorithm.
        algo_cls: The algorithm class implementing MazeAlgorithm.

    Returns:
        None
    """
    ALGORITHMS[name.lower()] = algo_cls


class MazeGenerator:
    """Manages the lifecycle of maze generation, application of configurations,

    animation steps, and solution pathfinding.
    """

    def __init__(self, config: MazeConfig):
        """Initializes the MazeGenerator with the
                                        specified configuration and seeded RNG.

        Args:
            config: The configuration object containing maze parameters.

        Returns:
            None
        """
        self.config = config
        self.rng = random.Random(config.seed)

    def create_maze(self, algorithm: MazeAlgorithm) -> Maze:
        """Generates a complete maze instance
                                    using the provided algorithm and rules.

        Args:
            algorithm: The algorithm instance used to build the maze layout.

        Returns:
            A fully generated and post-processed Maze instance.
        """
        maze = Maze(
            self.config.width,
            self.config.height,
            self.config.entry,
            self.config.exit
        )
        maze.apply_42_pattern()

        gen = algorithm.generate(maze, self.rng, self.config.entry)
        for _ in gen:
            pass

        if not self.config.perfect:
            maze.open_pacman_key_areas()
            maze.add_random_loops(
                self.rng,
                extra_passages=max(2, (maze.width * maze.height) // 20)
            )
        if self.config.no_dead_ends:
            maze.braid(self.rng)
        return maze

    def create_maze_animated(
        self,
        algorithm: MazeAlgorithm,
        renderer: BaseRenderer,
        color_scheme: int
    ) -> Maze:
        """Generates a maze dynamically with live terminal rendering steps.

        Args:
            algorithm: The algorithm instance used to build the maze layout.
            renderer: The renderer instance responsible for visual display.
            color_scheme:
                    The integer code representing, the active color palette.

        Returns:
            A fully generated Maze instance after
                                completing the animation steps.
        """
        maze = Maze(
            self.config.width,
            self.config.height,
            self.config.entry,
            self.config.exit
        )
        maze.apply_42_pattern()

        print("\033[H\033[J", end="")
        renderer.render(maze, None, color_scheme)
        time.sleep(0.02)

        gen = algorithm.generate(maze, self.rng, self.config.entry)
        for _ in gen:
            print("\033[H\033[J", end="")
            renderer.render(maze, None, color_scheme)
            time.sleep(0.005)

        if not self.config.perfect:
            maze.open_pacman_key_areas()
            maze.add_random_loops(
                self.rng,
                extra_passages=max(2, (maze.width * maze.height) // 20)
            )
        if self.config.no_dead_ends:
            maze.braid(self.rng)

        print("\033[H\033[J", end="")
        renderer.render(maze, None, color_scheme)
        return maze

    def get_solution(self, maze: Maze) -> List[str]:
        """Computes the shortest path from the entry
                            coordinate to the exit coordinate.

        Args:
            maze: The generated Maze instance to solve.

        Returns:
            A list of direction steps representing the solution path.

        Raises:
            PathNotFoundError: If no valid path exists between entry and exit.
        """
        path = solve_bfs(maze, self.config.entry, self.config.exit)
        if not path:
            raise PathNotFoundError("Impossible to achieve EXIT From ENTRY.")
        return path
