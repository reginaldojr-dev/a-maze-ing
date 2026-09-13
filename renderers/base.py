from abc import ABC, abstractmethod
from typing import List, Optional
from mazegen.maze import Maze


class BaseRenderer(ABC):
    """Abstract base class defining the standard interface for maze render."""

    @abstractmethod
    def render(
        self,
        maze: Maze,
        path: Optional[List[str]] = None,
        color_scheme: int = 0
    ) -> None:
        """Renders the maze structure and an optional solution path.

        Args:
            maze: The Maze instance to render.
            path: An optional list of direction steps representing the
                solution path.
            color_scheme: An integer code selecting the palette.

        Returns:
            None
        """
        pass
