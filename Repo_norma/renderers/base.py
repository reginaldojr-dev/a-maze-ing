from abc import ABC, abstractmethod
from typing import List, Optional
from mazegen.maze import Maze


class BaseRenderer(ABC):
    @abstractmethod
    def render(
        self,
        maze: Maze,
        path: Optional[List[str]] = None,
        color_scheme: int = 0
    ) -> None:
        pass
