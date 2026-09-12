from typing import List, Optional

from mazegen.maze import Maze
from mazegen.walls import Wall
from renderers.base import BaseRenderer


class ASCIIRenderer(BaseRenderer):
    def render(
        self,
        maze: Maze,
        path: Optional[List[str]] = None,
        color_scheme: int = 0
    ) -> None:

        COLOR_SCHEMES = {
            0: {
                "wall": "\033[0m",
                "path": "\033[32m",
                "reset": "\033[0m",
            },
            1: {
                "wall": "\033[34m",
                "path": "\033[33m",
                "reset": "\033[0m",
            },
            2: {
                "wall": "\033[31m",
                "path": "\033[36m",
                "reset": "\033[0m",
            },
            3: {
                "wall": "\033[35m",
                "path": "\033[32m",
                "reset": "\033[0m",
            },
        }

        colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES[0])
        w_color = colors["wall"]
        p_color = colors["path"]
        reset = colors["reset"]

        canvas_height = maze.height + 1
        canvas_width = maze.width * 2 + 1

        canvas = [
            [" " for _ in range(canvas_width)]
            for _ in range(canvas_height)
        ]

        for x in range(maze.width):
            canvas[0][x * 2 + 1] = f"{w_color}_{reset}"

        for y in range(maze.height):
            for x in range(maze.width):
                cell = maze.cell_at(x, y)

                draw_x = x * 2 + 1
                draw_y = y + 1

                if cell.has_wall(Wall.WEST):
                    canvas[draw_y][draw_x - 1] = f"{w_color}|{reset}"

                if cell.has_wall(Wall.EAST):
                    canvas[draw_y][draw_x + 1] = f"{w_color}|{reset}"

                if cell.has_wall(Wall.SOUTH):
                    canvas[draw_y][draw_x] = f"{w_color}_{reset}"

                if cell.is_blocked:
                    canvas[draw_y][draw_x] = "#"
                elif (x, y) == maze.entry:
                    canvas[draw_y][draw_x] = "E"
                elif (x, y) == maze.exit:
                    canvas[draw_y][draw_x] = "X"

        if path:
            curr_x, curr_y = maze.entry

            for direction in path:
                if direction == "N":
                    curr_y -= 1
                elif direction == "S":
                    curr_y += 1
                elif direction == "E":
                    curr_x += 1
                elif direction == "W":
                    curr_x -= 1

                if (
                    (curr_x, curr_y)
                    != maze.exit
                    and (curr_x, curr_y)
                    != maze.entry
                ):
                    draw_x = curr_x * 2 + 1
                    draw_y = curr_y + 1
                    canvas[draw_y][draw_x] = f"{p_color}*{reset}"

        for row in canvas:
            print("".join(row))
        print()
