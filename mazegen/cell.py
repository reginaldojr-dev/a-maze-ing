from mazegen.walls import Wall


class Cell:
    """Represents an individual grid coordinate unit, tracking its position,

    walls state via bitwise flags, and whether it belongs to a blocked pattern.
    """

    def __init__(self, x: int, y: int):
        """Initializes a Cell at the given coordinate with all walls intact.

        Args:
            x: The horizontal grid coordinate index.
            y: The vertical grid coordinate index.

        Returns:
            None
        """
        self.x = x
        self.y = y
        self.walls = Wall.ALL
        self.is_blocked = False

    def remove_wall(self, wall: Wall) -> None:
        """Remove a specif wall flag from the cell using bitwise operations.

        Args:
            wall: The Wall flag to clear.

        Returns:
            None
        """
        self.walls &= ~wall

    def add_wall(self, wall: Wall) -> None:
        """Adds a specified wall flag to the cell using bitwise operations.

        Args:
            wall: The Wall flag to set.

        Returns:
            None
        """
        self.walls |= wall

    def has_wall(self, wall: Wall) -> bool:
        """Checks if a specified wall is currently present on the cell.

        Args:
            wall: The Wall flag to check.

        Returns:
            True if the wall exists, False otherwise.
        """
        return bool(self.walls & wall)

    def wall_count(self) -> int:
        """Counts the total number of standing walls surrounding the cell.

        Returns:
            The integer count of active walls.
        """
        count = 0
        w = int(self.walls)
        while w > 0:
            count += w & 1
            w >>= 1
        return count
