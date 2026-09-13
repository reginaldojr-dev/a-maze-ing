import random
from typing import Generator, List, Tuple
from mazegen.cell import Cell
from mazegen.walls import Wall


class Maze:
    """Represents the complete maze structure, managing the grid matrix,

    walls, boundaries, special patterns, and braiding operations.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int]
    ):
        """Initializes the Maze grid with dimensions, entry, and exit points.

        Args:
            width: The total number of columns in the maze.
            height: The total number of rows in the maze.
            entry: The coordinate tuple (x, y) marking the maze entry.
            exit: The coordinate tuple (x, y) marking the maze exit.

        Returns:
            None
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.grid: List[List[Cell]] = [
            [Cell(x, y) for x in range(width)] for y in range(height)
        ]

    def cell_at(self, x: int, y: int) -> Cell:
        """Retrieves the Cell instance at the specified coordinate position.

        Args:
            x: The horizontal grid index.
            y: The vertical grid index.

        Returns:
            The Cell object located at (x, y).
        """
        return self.grid[y][x]

    def is_valid_coord(self, x: int, y: int) -> bool:
        """Checks if the given coordinate falls within the valid maze bounds.

        Args:
            x: The horizontal grid index.
            y: The vertical grid index.

        Returns:
            True if the coordinate is inside the grid, False otherwise.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def open_passage(self, x: int, y: int, direction: Wall) -> None:
        """Removes the wall between a cell and its
                                        neighbor in a given direction.

        Args:
            x: The horizontal grid index of the origin cell.
            y: The vertical grid index of the origin cell.
            direction: The Wall direction indicating the passage side.

        Returns:
            None
        """
        dx, dy = 0, 0
        if direction == Wall.NORTH:
            dy = -1
        elif direction == Wall.SOUTH:
            dy = 1
        elif direction == Wall.EAST:
            dx = 1
        elif direction == Wall.WEST:
            dx = -1
        nx, ny = x + dx, y + dy
        if self.is_valid_coord(nx, ny):
            self.cell_at(x, y).remove_wall(direction)
            self.cell_at(nx, ny).remove_wall(direction.opposite)

    def get_neighbor_coords(
        self,
        x: int,
        y: int
    ) -> Generator[Tuple[Wall, Tuple[int, int]], None, None]:
        """Yields valid neighboring coordinates and their relative directions.

        Args:
            x: The horizontal grid index.
            y: The vertical grid index.

        Returns:
            A generator yielding tuples of (Wall direction, (neighbor x, y)).
        """
        directions = [
            (Wall.NORTH, (x, y - 1)),
            (Wall.EAST, (x + 1, y)),
            (Wall.SOUTH, (x, y + 1)),
            (Wall.WEST, (x - 1, y)),
        ]
        for direction, (nx, ny) in directions:
            if self.is_valid_coord(nx, ny):
                yield direction, (nx, ny)

    def apply_42_pattern(self) -> None:
        """Applies the mandatory '42' blocked structural pattern onto the grid.

        Returns:
            None
        """
        pattern = [
            "1000101111",
            "1000100001",
            "1111101111",
            "0000101000",
            "0000101111",
        ]
        pw, ph = 10, 5

        if self.width < pw or self.height < ph:
            return

        pad_x = self.width - pw
        pad_y = self.height - ph

        start_x = pad_x // 2
        start_y = pad_y // 2

        for row_idx, row_str in enumerate(pattern):
            for col_idx, char in enumerate(row_str):
                if char == "1":
                    gx = start_x + col_idx
                    gy = start_y + row_idx

                    if (
                        self.is_valid_coord(gx, gy)
                        and (gx, gy) != self.entry
                        and (gx, gy) != self.exit
                    ):
                        self.cell_at(gx, gy).is_blocked = True

    def open_pacman_key_areas(self) -> None:
        """Opens key transition areas in corners and center for Pac-Man mode.

        Returns:
            None
        """
        corners = [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1)
        ]
        center = (self.width // 2, self.height // 2)

        for cx, cy in corners + [center]:
            if not self.cell_at(cx, cy).is_blocked:
                for d, (nx, ny) in self.get_neighbor_coords(cx, cy):
                    if not self.cell_at(nx, ny).is_blocked:
                        self.open_passage(cx, cy, d)

    def add_random_loops(
        self,
        rng: random.Random,
        extra_passages: int
    ) -> None:
        """Introduces random alternative passages to create loops in the maze.

        Args:
            rng: The random number generator instance.
            extra_passages: The target number of extra passages to open.

        Returns:
            None
        """
        count = 0
        attempts = 0
        max_attempts = 200

        while count < extra_passages and attempts < max_attempts:
            attempts += 1
            rx = rng.randint(0, self.width - 1)
            ry = rng.randint(0, self.height - 1)
            cell = self.cell_at(rx, ry)
            if cell.is_blocked:
                continue
            valid_neighbors = [
                (d, coords) for d, coords in self.get_neighbor_coords(rx, ry)
                if not self.cell_at(coords[0], coords[1]).is_blocked
            ]
            if valid_neighbors:
                direction, (nx, ny) = rng.choice(valid_neighbors)
                if cell.has_wall(direction):
                    self.open_passage(rx, ry, direction)
                    count += 1

    def braid(self, rng: random.Random) -> None:
        """Iteratively removes dead-end cells to achieve a perfectly braided.

        Args:
            rng: The random number generator instance.

        Returns:
            None
        """
        while True:
            dead_ends = []
            for y in range(self.height):
                for x in range(self.width):
                    cell = self.cell_at(x, y)
                    if not cell.is_blocked and cell.wall_count() == 3:
                        dead_ends.append((x, y))

            if not dead_ends:
                break

            rng.shuffle(dead_ends)
            carve_made = False
            for x, y in dead_ends:
                cell = self.cell_at(x, y)
                if cell.wall_count() != 3:
                    continue
                dead_end_walls = [
                    d for d in [Wall.NORTH, Wall.EAST, Wall.SOUTH, Wall.WEST]
                    if cell.has_wall(d)
                ]
                rng.shuffle(dead_end_walls)
                for d in dead_end_walls:
                    for check_d, (nx, ny) in self.get_neighbor_coords(x, y):
                        if (
                            check_d == d
                            and not self.cell_at(nx, ny).is_blocked
                        ):
                            self.open_passage(x, y, d)
                            carve_made = True
                            break
                    if cell.wall_count() < 3:
                        break
            if not carve_made:
                break

    def export_hex_format(self) -> List[str]:
        """Encodes the maze cell walls into a sequence of hexadecimal string.

        Returns:
            A list of strings representing each row in hexadecimal format.
        """
        lines = []
        for y in range(self.height):
            row_hex = []
            for x in range(self.width):
                cell = self.cell_at(x, y)
                if cell.is_blocked:
                    row_hex.append("F")
                else:
                    row_hex.append(f"{int(cell.walls):X}")
            lines.append("".join(row_hex))
        return lines
