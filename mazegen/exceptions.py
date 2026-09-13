class MazeError(Exception):
    """Base exception class for all maze-related errors."""

    pass


class ConfigError(MazeError):
    """Exception raised for errors concerning config parsing or validation."""

    pass


class GenerationError(MazeError):
    """Exception raised when an error occurs during maze generation."""

    pass


class PathNotFoundError(MazeError):
    """Except raised when no valid path can be found between entry and exit."""

    pass
