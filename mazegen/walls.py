from enum import IntFlag


class Wall(IntFlag):
    NONE = 0
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8
    ALL = 15

    @property
    def opposite(self) -> "Wall":
        if self == Wall.NORTH:
            return Wall.SOUTH
        if self == Wall.SOUTH:
            return Wall.NORTH
        if self == Wall.EAST:
            return Wall.WEST
        if self == Wall.WEST:
            return Wall.EAST
        return Wall.NONE
