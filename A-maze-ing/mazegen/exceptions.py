class MazeError(Exception):
    pass


class ConfigError(MazeError):
    pass


class GenerationError(MazeError):
    pass


class PathNotFoundError(MazeError):
    pass
