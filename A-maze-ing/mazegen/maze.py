from typing import List, Tuple, Generator
from mazegen.cell import Cell
from mazegen.walls import Wall
import random


class Maze:
    def __init__(self, width: int, height: int, entry: Tuple[int, int], exit: Tuple[int, int]):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.grid: List[List[Cell]] = [
            [Cell(x, y) for x in range(width)] for y in range(height)
        ]

    def cell_at(self, x: int, y: int) -> Cell:
        return self.grid[y][x]

    def is_valid_coord(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def open_passage(self, x: int, y: int, direction: Wall) -> None:
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

    def get_neighbor_coords(self, x: int, y: int) -> Generator[Tuple[Wall, Tuple[int, int]], None, None]:
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
        pattern = [
            "1000101111",
            "1000100001",
            "1111101111",
            "0000101000",
            "0000101111"
        ]
        pw, ph = 10, 5
        if self.width < pw + 4 or self.height < ph + 4:
            return

        start_x = (self.width - pw) // 2
        start_y = (self.height - ph) // 2

        for row_idx, row_str in enumerate(pattern):
            for col_idx, char in enumerate(row_str):
                if char == "1":
                    gx = start_x + col_idx
                    gy = start_y + row_idx
                    if (gx, gy) != self.entry and (gx, gy) != self.exit:
                        self.cell_at(gx, gy).is_blocked = True

    def ensure_pacman_intersections(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cell_at(x, y)
                if not cell.is_blocked:
                    cell.remove_wall(Wall.NORTH)
                    cell.remove_wall(Wall.SOUTH)
                    cell.remove_wall(Wall.EAST)
                    cell.remove_wall(Wall.WEST)

    def add_random_loops(self, rng: random.Random, extra_passages: int) -> None:
        count = 0
        attempts = 0
        max_attempts = 100

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
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cell_at(x, y)
                if cell.is_blocked:
                    continue
                if cell.wall_count() == 3:
                    dead_end_walls = [
                        d for d in [Wall.NORTH, Wall.EAST, Wall.SOUTH, Wall.WEST]
                        if cell.has_wall(d)
                    ]
                    rng.shuffle(dead_end_walls)
                    for d in dead_end_walls:
                        for check_d, (nx, ny) in self.get_neighbor_coords(x, y):
                            if check_d == d and not self.cell_at(nx, ny).is_blocked:
                                self.open_passage(x, y, d)
                                break
                        if cell.wall_count() < 3:
                            break

    def export_hex_format(self) -> List[str]:
        lines = []
        for y in range(self.height):
            row_hex = []
            for x in range(self.width):
                cell = self.cell_at(x, y)
                if cell.is_blocked:
                    row_hex.append("F")
                else:
                    row_hex.append(".")
            lines.append("".join(row_hex))
        return lines