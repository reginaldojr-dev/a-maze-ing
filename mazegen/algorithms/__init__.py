from typing import Dict, Type
from mazegen.algorithms.base import MazeAlgorithm
from mazegen.algorithms.backtracker import RecursiveBacktracker
from mazegen.algorithms.prim import PrimAlgorithm
from mazegen.algorithms.kruskal import KruskalAlgorithm

ALGORITHMS: Dict[str, Type[MazeAlgorithm]] = {
    "backtracker": RecursiveBacktracker,
    "prim": PrimAlgorithm,
    "kruskal": KruskalAlgorithm,
}


def get_algorithm(name: str) -> MazeAlgorithm:
    algo_cls = ALGORITHMS.get(name.lower())
    if not algo_cls:
        raise ValueError(f"Algoritmo '{name}' desconhecido.")
    return algo_cls()
