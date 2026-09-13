import os
import sys
import random
import time
from typing import Dict, Type, List, Optional, Generator

from mazegen.config import MazeConfig
from mazegen.generator import MazeGenerator
from mazegen.exceptions import MazeError, ConfigError, PathNotFoundError
from mazegen.algorithms.base import MazeAlgorithm
from renderers.base import BaseRenderer
from mazegen.maze import Maze
from mazegen.walls import Wall


def clean_exit() -> None:
    """ Restores the terminal cursor (if it has been hidden in animations)"""
    sys.stdout.write("\033[999;1H\033[?25h")
    sys.stdout.flush()
    print("\n[!] Execution stopped by the user..")


def validate_terminal_size(width: int, height: int) -> None:
    try:
        term_size = os.get_terminal_size()
        min_cols = width * 2 + 1
        min_rows = height + 6
        if term_size.columns < min_cols or term_size.lines < min_rows:
            print(
                f"[ERRO DE TELA] Terminal muito pequeno. "
                f"Necessário: {min_cols}x{min_rows}, "
                f"Atual: {term_size.columns}x{term_size.lines}",
                file=sys.stderr
            )
            sys.exit(1)
    except OSError:
        pass


class FallbackAlgorithm(MazeAlgorithm):
    """Provides a basic fallback algorithm that carves every available pass."""

    def generate(
        self,
        maze: Maze,
        rng: random.Random,
        start_pos: tuple
    ) -> Generator[Maze, None, None]:
        """Carves straight horizontal and vertical passages sequentially.

        Args:
            maze: The Maze instance to modify.
            rng: The random number generator instance.
            start_pos: The starting coordinate tuple (x, y).

        Returns:
            A generator yielding the modified Maze instance.
        """
        for y in range(maze.height):
            for x in range(maze.width):
                cell = maze.cell_at(x, y)
                if not cell.is_blocked:
                    if (
                        x < maze.width - 1
                        and not maze.cell_at(x + 1, y).is_blocked
                    ):
                        maze.open_passage(x, y, Wall.EAST)
                    if (
                        y < maze.height - 1
                        and not maze.cell_at(x, y + 1).is_blocked
                    ):
                        maze.open_passage(x, y, Wall.SOUTH)
        yield maze


class FallbackRenderer(BaseRenderer):
    """Provides a fallback text renderer that prints hexadec maze struct."""

    def render(
        self,
        maze: Maze,
        path: Optional[List[str]] = None,
        color_scheme: int = 0
    ) -> None:
        """Renders the maze as hexadec lines and displays solution step counts.

        Args:
            maze: The Maze instance to render.
            path: An optional list of solution step strings.
            color_scheme: An integer representing the active color palette.

        Returns:
            None
        """
        print(f"\n--- [RENDERER FALLBACK - PALETA {color_scheme}] ---")
        for line in maze.export_hex_format():
            print(line)
        if path:
            print(
                f"\nPath Solution ({len(path)} steps): "
                f"{''.join(path)}"
            )
        print("-----------------------------------------\n")


ALGORITHMS: Dict[str, Type[MazeAlgorithm]] = {
    "backtracker": FallbackAlgorithm,
    "prim": FallbackAlgorithm,
    "kruskal": FallbackAlgorithm,
}

RENDERERS: Dict[str, Type[BaseRenderer]] = {
    "ascii": FallbackRenderer,
}

try:
    from mazegen.algorithms.backtracker import RecursiveBacktracker
    ALGORITHMS["backtracker"] = RecursiveBacktracker
except ImportError:
    pass

try:
    from mazegen.algorithms.prim import PrimAlgorithm
    ALGORITHMS["prim"] = PrimAlgorithm
except ImportError:
    pass

try:
    from mazegen.algorithms.kruskal import KruskalAlgorithm
    ALGORITHMS["kruskal"] = KruskalAlgorithm
except ImportError:
    pass

try:
    from renderers.ascii_renderer import ASCIIRenderer
    RENDERERS["ascii"] = ASCIIRenderer
except ImportError:
    pass


def save_output_file(
    filepath: str,
    maze: Maze,
    entry: tuple,
    exit_pos: tuple,
    path: List[str]
) -> None:
    """Saves the generat maze struct, entry, exit, and solution path to a file.

    Args:
        filepath: The destination file path where output is written.
        maze: The Maze instance containing the grid data.
        entry: The coordinate tuple (x, y) marking the entry point.
        exit_pos: The coordinate tuple (x, y) marking the exit point.
        path: A list of direction step strings representing the solution.

    Returns:
        None
    """
    with open(filepath, "w", encoding="utf-8") as f:
        for line in maze.export_hex_format():
            f.write(line + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit_pos[0]},{exit_pos[1]}\n")
        f.write("".join(path) + "\n")


def interactive_loop(
    config: MazeConfig,
    renderer: BaseRenderer,
    algorithm: MazeAlgorithm
) -> None:
    """Manages the interactive terminal loop for maze generation,
             render, and controls.

    Args:
        config: The MazeConfig instance with parameters.
        renderer: The renderer instance used for display.
        algorithm: The maze generation algorithm instance.

    Returns:
        None
    """
    generator = MazeGenerator(config)
    show_path = True
    color_scheme = 0

    maze = generator.create_maze_animated(algorithm, renderer, color_scheme)
    path = generator.get_solution(maze)
    save_output_file(
        config.output_file,
        maze,
        config.entry,
        config.exit,
        path
    )

    if show_path:
        partial_path = []
        for step in path:
            partial_path.append(step)
            print("\033[H\033[J", end="")
            renderer.render(maze, partial_path, color_scheme)
            time.sleep(0.08)

    while True:
        print("\033[H\033[J", end="")
        renderer.render(maze, path if show_path else None, color_scheme)

        print("--- A-Maze-ing Menu ---")
        print("1. Re-generate a new maze")
        print("2. Show/Hide shortest path")
        print("3. Change wall colors")
        print("4. Quit")

        try:
            choice = input("Choice (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == "1":
            new_seed = int.from_bytes(os.urandom(4), "big")
            config = MazeConfig(
                width=config.width,
                height=config.height,
                entry=config.entry,
                exit=config.exit,
                output_file=config.output_file,
                perfect=config.perfect,
                seed=new_seed,
                algorithm=config.algorithm,
                display=config.display,
                no_dead_ends=config.no_dead_ends,
            )
            generator = MazeGenerator(config)
            maze = generator.create_maze_animated(
                algorithm,
                renderer,
                color_scheme
            )
            path = generator.get_solution(maze)
            save_output_file(
                config.output_file,
                maze,
                config.entry,
                config.exit,
                path
            )

            if show_path:
                partial_path = []
                for step in path:
                    partial_path.append(step)
                    print("\033[H\033[J", end="")
                    renderer.render(maze, partial_path, color_scheme)
                    time.sleep(0.08)

        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_scheme = (color_scheme + 1) % 4
        elif choice == "4":
            break


def main() -> None:
    """Executes the main entry point for the A-Maze-ing application.

    Returns:
        None
    """
    if len(sys.argv) != 2:
        print(
            f"Use: python3 {sys.argv[0]} <path_of_config.txt>",
            file=sys.stderr,
        )
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        config = MazeConfig.from_file(config_path)
        validate_terminal_size(config.width, config.height)

        algo_cls = ALGORITHMS.get(config.algorithm)
        if not algo_cls:
            raise ConfigError(
                f"Algorithm '{config.algorithm}' not supported."
            )
        algorithm = algo_cls()

        renderer_cls = RENDERERS.get(config.display)
        if not renderer_cls:
            raise ConfigError(
                f"Display '{config.display}' not supported."
            )
        renderer = renderer_cls()

        interactive_loop(config, renderer, algorithm)

    except KeyboardInterrupt:
        clean_exit()
        sys.exit(0)
    except ConfigError as e:
        print(f"[ERROR CONFIG] {e}", file=sys.stderr)
        sys.exit(1)
    except PathNotFoundError as e:
        print(f"[ERROR SOLUTION] {e}", file=sys.stderr)
        sys.exit(1)
    except MazeError as e:
        print(f"[ERROR DOMAIN] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR UNEXPECTED] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
