import sys
import random
from typing import Dict, Type, List, Optional
from typing import Generator

from mazegen.config import MazeConfig
from mazegen.generator import MazeGenerator
from mazegen.exceptions import MazeError, ConfigError, PathNotFoundError
from mazegen.algorithms.base import MazeAlgorithm
from renderers.base import BaseRenderer
from mazegen.maze import Maze
from mazegen.walls import Wall


# =====================================================================
# FALLBACKS LOCAIS (Para testar o projeto de forma autonoma)
# =====================================================================

class FallbackAlgorithm(MazeAlgorithm):
    def generate(
        self,
        maze: Maze,
        rng: random.Random,
        start_pos: tuple
    ) -> Generator[Maze, None, None]:
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
    """Exibe o labirinto em formato hexadecimal simples no terminal."""
    def render(self, maze: Maze, path: Optional[List[str]] = None) -> None:
        print("\n--- [RENDERER FALLBACK - MATRIZ HEX] ---")
        for line in maze.export_hex_format():
            print(line)
        if path:
            print(
                f"\nCaminho Solucao ({len(path)} passos): "
                f"{' -> '.join(path)}",
            )
        print("-----------------------------------------\n")


# =====================================================================
# REGISTRO DE MODULOS (modulos do regi pluga as implementacoes aqui)
# =====================================================================

ALGORITHMS: Dict[str, Type[MazeAlgorithm]] = {
    "backtracker": FallbackAlgorithm,
    "prim": FallbackAlgorithm,
    "kruskal": FallbackAlgorithm,
}

RENDERERS: Dict[str, Type[BaseRenderer]] = {
    "ascii": FallbackRenderer,
    "mlx": FallbackRenderer,
}


# Tenta carregar as implementacoes reais do regi se ja existirem
try:
    from mazegen.algorithms.backtracker import BacktrackerAlgorithm
    ALGORITHMS["backtracker"] = BacktrackerAlgorithm
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

try:
    from renderers.mlx_renderer import MLXRenderer
    RENDERERS["mlx"] = MLXRenderer
except ImportError:
    pass


# =====================================================================
# ENTRY POINT
# =====================================================================

def main() -> None:
    if len(sys.argv) != 2:
        print(
            f"Use: python3 {sys.argv[0]} <path_of_config.txt>",
            file=sys.stderr,
        )
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        """1. Configuration File Parsing"""
        config = MazeConfig.from_file(config_path)

        """2. Dynamic Algorithm Resolution"""
        algo_cls = ALGORITHMS.get(config.algorithm)
        if not algo_cls:
            raise ConfigError(f"Algorit '{config.algorithm}' no suport.")
        algorithm = algo_cls()

        """3. Labyrinth Generation"""
        generator = MazeGenerator(config)
        maze = generator.create_maze(algorithm)

        """4. Solution of maze (BFS)"""
        solution_path = generator.get_solution(maze)

        """5. Export of Hexadecimal Array to File"""
        hex_data = maze.export_hex_format()
        with open(config.output_file, "w", encoding="utf-8") as f:
            for line in hex_data:
                f.write(line + "\n")

        """6. Visual Rendering"""
        renderer_cls = RENDERERS.get(config.display)
        if not renderer_cls:
            raise ConfigError(f"Show'{config.display}' no suport.")
        renderer = renderer_cls()
        renderer.render(maze, solution_path)

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
