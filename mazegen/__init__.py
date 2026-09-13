"""Init module for the mazegen pkg,exposing core class and exceptions."""

from mazegen.maze import Maze
from mazegen.config import MazeConfig
from mazegen.generator import MazeGenerator
from mazegen.exceptions import MazeError, ConfigError

__all__ = ["Maze", "MazeConfig", "MazeGenerator", "MazeError", "ConfigError"]
