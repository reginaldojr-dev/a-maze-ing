from typing import List, Optional

from mazegen.maze import Maze
from mazegen.walls import Wall
from renderers.base import BaseRenderer


class ASCIIRenderer(BaseRenderer):
    def render(
        self,
        maze: Maze,
        path: Optional[List[str]] = None
    ) -> None:

        canvas_height = maze.height + 1
        canvas_width = maze.width * 2 + 1

        canvas = [
            [" " for _ in range(canvas_width)]
            for _ in range(canvas_height)
        ]

        for x in range(1, canvas_width, 2):
            canvas[0][x] = "_"

        for y in range(maze.height):
            for x in range(maze.width):
                cell = maze.cell_at(x, y)

                draw_x = x * 2 + 1
                draw_y = y + 1

                if cell.has_wall(Wall.WEST):
                    canvas[draw_y][draw_x - 1] = "|"

                if cell.has_wall(Wall.EAST):
                    canvas[draw_y][draw_x + 1] = "|"

                if cell.has_wall(Wall.SOUTH):
                    canvas[draw_y][draw_x] = "_"

                if cell.is_blocked:
                    canvas[draw_y][draw_x] = "#"
                elif (x, y) == maze.entry:
                    canvas[draw_y][draw_x] = "E"
                elif (x, y) == maze.exit:
                    canvas[draw_y][draw_x] = "X"

        if path:
            path_x, path_y = maze.entry

            for direction in path:
                if direction == "N":
                    path_y -= 1
                elif direction == "S":
                    path_y += 1
                elif direction == "E":
                    path_x += 1
                elif direction == "W":
                    path_x -= 1

                draw_x = path_x * 2 + 1
                draw_y = path_y + 1

                if (path_x, path_y) != maze.exit:
                    canvas[draw_y][draw_x] = "■"

        for row in canvas:
            print("".join(row))
