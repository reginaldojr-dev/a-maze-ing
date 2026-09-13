from typing import List, Optional

from mazegen.maze import Maze
from mazegen.walls import Wall
from renderers.base import BaseRenderer


class ASCIIRenderer(BaseRenderer):
    """Renders the maze and solution path in the terminal using ASCII char

    and ANSI color codes.
    """

    def render(
        self,
        maze: Maze,
        path: Optional[List[str]] = None,
        color_scheme: int = 0
    ) -> None:
        """Render the maze grid, entry, exit, walls, and option solution path.

        Args:
            maze: The Maze instance to render.
            path: An optional list of direction steps representing the
                solution path.
            color_scheme: An integer code selecting the active color palette.

        Returns:
            None
        """

        COLOR_SCHEMES = {
            0: {
                "wall": "\033[40;34m",
                "path": "\033[40;33m",
                "space": "\033[40m \033[0m",
                "block": "\033[47m \033[0m",
                "reset": "\033[0m",
            },
            1: {
                "wall": "\033[40;37m",
                "path": "\033[40;32m",
                "space": "\033[40m \033[0m",
                "block": "\033[47m \033[0m",
                "reset": "\033[0m",
            },
            2: {
                "wall": "\033[40;31m",
                "path": "\033[40;36m",
                "space": "\033[40m \033[0m",
                "block": "\033[47m \033[0m",
                "reset": "\033[0m",
            },
            3: {
                "wall": "\033[40;35m",
                "path": "\033[40;32m",
                "space": "\033[40m \033[0m",
                "block": "\033[47m \033[0m",
                "reset": "\033[0m",
            },
        }

        colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES[0])
        w_color = colors["wall"]
        p_color = colors["path"]
        b_space = colors["space"]
        b_block = colors["block"]
        reset = colors["reset"]

        canvas_height = maze.height + 1
        canvas_width = maze.width * 2 + 1

        canvas = [
            [b_space for _ in range(canvas_width)]
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
                    canvas[draw_y][draw_x] = b_block
                elif (x, y) == maze.entry:
                    canvas[draw_y][draw_x] = f"\033[40;32mE{reset}"
                elif (x, y) == maze.exit:
                    canvas[draw_y][draw_x] = f"\033[40;31mX{reset}"

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
