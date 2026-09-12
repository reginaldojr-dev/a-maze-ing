from typing import Any, Callable, List, Optional

from mlx import Mlx

from mazegen.cell import Cell
from mazegen.maze import Maze
from mazegen.walls import Wall
from renderers.base import BaseRenderer


RegenerateCallback = Callable[[], tuple[Maze, List[str]]]


class MLXRenderer(BaseRenderer):
    ESC_KEY = 65307
    KEY_P = 112
    KEY_C = 99
    KEY_R = 114

    def __init__(self) -> None:
        self.mlx = Mlx()

        self.mlx_ptr: Any = None
        self.window: Any = None

        self.maze: Optional[Maze] = None
        self.path: Optional[List[str]] = None

        self.cell_size = 30
        self.show_path = True

        self.wall_colors = [
            0xFFFFFFFF,
            0xFF00FF88,
            0xFF00AAFF,
            0xFFFFAA00,
            0xFFFF66CC,
        ]

        self.wall_color_index = 0
        self.wall_color = self.wall_colors[0]

        self.path_color = 0xFFFFFF00
        self.entry_color = 0xFF00CC66
        self.exit_color = 0xFFFF4444
        self.pattern_color = 0xFF777777

        self.regenerate_callback: Optional[
            RegenerateCallback
        ] = None

    def set_regenerate_callback(
        self,
        callback: RegenerateCallback
    ) -> None:
        self.regenerate_callback = callback

    def render(
        self,
        maze: Maze,
        path: Optional[List[str]] = None
    ) -> None:
        self.maze = maze
        self.path = path

        window_width = maze.width * self.cell_size + 1
        window_height = maze.height * self.cell_size + 1

        self.mlx_ptr = self.mlx.mlx_init()

        if self.mlx_ptr is None:
            raise RuntimeError(
                "Falha ao inicializar a MiniLibX."
            )

        self.window = self.mlx.mlx_new_window(
            self.mlx_ptr,
            window_width,
            window_height,
            "A-Maze-ing"
        )

        if self.window is None:
            raise RuntimeError(
                "Falha ao criar a janela MLX."
            )

        self._register_hooks()
        self._redraw()

        self.mlx.mlx_loop(self.mlx_ptr)

        self._release()

    def _register_hooks(self) -> None:
        self.mlx.mlx_key_hook(
            self.window,
            self._handle_key,
            None
        )

        self.mlx.mlx_hook(
            self.window,
            33,
            0,
            self._handle_close,
            None
        )

    def _redraw(self) -> None:
        if self.maze is None:
            return

        self.mlx.mlx_clear_window(
            self.mlx_ptr,
            self.window
        )

        self._draw_special_cells()

        if self.show_path and self.path:
            self._draw_path()

        self._draw_walls()

    def _draw_walls(self) -> None:
        if self.maze is None:
            return

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.cell_at(x, y)

                self._draw_cell_walls(cell)

    def _draw_cell_walls(
        self,
        cell: Cell
    ) -> None:
        left = cell.x * self.cell_size
        top = cell.y * self.cell_size

        right = left + self.cell_size
        bottom = top + self.cell_size

        if cell.has_wall(Wall.NORTH):
            self._draw_horizontal_line(
                left,
                right,
                top,
                self.wall_color
            )

        if cell.has_wall(Wall.SOUTH):
            self._draw_horizontal_line(
                left,
                right,
                bottom,
                self.wall_color
            )

        if cell.has_wall(Wall.WEST):
            self._draw_vertical_line(
                left,
                top,
                bottom,
                self.wall_color
            )

        if cell.has_wall(Wall.EAST):
            self._draw_vertical_line(
                right,
                top,
                bottom,
                self.wall_color
            )

    def _draw_horizontal_line(
        self,
        x1: int,
        x2: int,
        y: int,
        color: int
    ) -> None:
        for x in range(x1, x2 + 1):
            self.mlx.mlx_pixel_put(
                self.mlx_ptr,
                self.window,
                x,
                y,
                color
            )

    def _draw_vertical_line(
        self,
        x: int,
        y1: int,
        y2: int,
        color: int
    ) -> None:
        for y in range(y1, y2 + 1):
            self.mlx.mlx_pixel_put(
                self.mlx_ptr,
                self.window,
                x,
                y,
                color
            )

    def _draw_special_cells(self) -> None:
        if self.maze is None:
            return

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.cell_at(x, y)

                if cell.is_blocked:
                    self._fill_cell(
                        cell,
                        self.pattern_color
                    )

        entry_cell = self.maze.cell_at(
            *self.maze.entry
        )

        exit_cell = self.maze.cell_at(
            *self.maze.exit
        )

        self._fill_cell(
            entry_cell,
            self.entry_color
        )

        self._fill_cell(
            exit_cell,
            self.exit_color
        )

    def _fill_cell(
        self,
        cell: Cell,
        color: int
    ) -> None:
        left = (
            cell.x * self.cell_size + 2
        )
        top = (
            cell.y * self.cell_size + 2
        )

        right = (
            (cell.x + 1) * self.cell_size - 2
        )
        bottom = (
            (cell.y + 1) * self.cell_size - 2
        )

        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                self.mlx.mlx_pixel_put(
                    self.mlx_ptr,
                    self.window,
                    x,
                    y,
                    color
                )

    def _draw_path(self) -> None:
        if (
            self.maze is None
            or self.path is None
        ):
            return

        path_x, path_y = self.maze.entry

        for direction in self.path:
            if direction == "N":
                path_y -= 1
            elif direction == "S":
                path_y += 1
            elif direction == "E":
                path_x += 1
            elif direction == "W":
                path_x -= 1

            if (
                (path_x, path_y)
                == self.maze.exit
            ):
                continue

            self._draw_path_marker(
                path_x,
                path_y
            )

    def _draw_path_marker(
        self,
        x: int,
        y: int
    ) -> None:
        center_x = (
            x * self.cell_size
            + self.cell_size // 2
        )

        center_y = (
            y * self.cell_size
            + self.cell_size // 2
        )

        marker_size = max(
            2,
            self.cell_size // 6
        )

        for py in range(
            center_y - marker_size,
            center_y + marker_size + 1
        ):
            for px in range(
                center_x - marker_size,
                center_x + marker_size + 1
            ):
                self.mlx.mlx_pixel_put(
                    self.mlx_ptr,
                    self.window,
                    px,
                    py,
                    self.path_color
                )

    def _handle_key(
        self,
        key: int,
        param: Any
    ) -> None:
        _ = param

        if key == self.ESC_KEY:
            self._close()

        elif key == self.KEY_P:
            self.show_path = not self.show_path
            self._redraw()

        elif key == self.KEY_C:
            self._cycle_wall_color()
            self._redraw()

        elif key == self.KEY_R:
            self._regenerate()

    def _cycle_wall_color(self) -> None:
        self.wall_color_index += 1

        self.wall_color_index %= len(
            self.wall_colors
        )

        self.wall_color = self.wall_colors[
            self.wall_color_index
        ]

    def _regenerate(self) -> None:
        if self.regenerate_callback is None:
            return

        maze, path = self.regenerate_callback()

        self.maze = maze
        self.path = path

        self._redraw()

    def _handle_close(
        self,
        param: Any
    ) -> None:
        _ = param
        self._close()

    def _close(self) -> None:
        if self.mlx_ptr is not None:
            self.mlx.mlx_loop_exit(
                self.mlx_ptr
            )

    def _release(self) -> None:
        if (
            self.mlx_ptr is None
            or self.window is None
        ):
            return

        self.mlx.mlx_destroy_window(
            self.mlx_ptr,
            self.window
        )

        self.mlx.mlx_release(
            self.mlx_ptr
        )
