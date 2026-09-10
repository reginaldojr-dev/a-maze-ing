from abc import ABC, abstractmethod
from typing import List, Optional
from mazegen.maze import Maze


class BaseRenderer(ABC):
    @abstractmethod
    def render(self, maze: Maze, path: Optional[List[str]] = None) -> None:
        pass