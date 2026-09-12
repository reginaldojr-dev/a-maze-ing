import ctypes
from pathlib import Path
from typing import Callable, List, Optional, TypeAlias

from mazegen.cell import Cell
from mazegen.maze import Maze
from mazegen.walls import Wall
from renderers.base import BaseRenderer

BufferPtr: TypeAlias = ctypes.c_char_p

# Callbacks prototipadas segundo a C-API do X11/MLX
KeyProto = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_void_p)
DestroyProto = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)


class MLXRenderer(BaseRenderer):

    COLOR_PALETTES = [
        (0x282828, 0xF0F0F0, 0x2ECC71, 0x3498DB, 0xE74C3C),
        (0x3B4252, 0xD8DEE9, 0xA3BE8C, 0x88C0D0, 0xBF616A),
        (0x1E1E1E, 0xD4D4D4, 0x4EC9B0, 0x569CD6, 0xF44747),
    ]

    def __init__(
        self,
        cell_size: int = 32,
        regenerate_callback: Optional[Callable[[], Maze]] = None,
    ) -> None:
        self.cell_size: int = cell_size
        self.regenerate_callback = regenerate_callback
        self.color_scheme_idx: int = 0
        self.show_path_flag: bool = True
        self.mlx: ctypes.CDLL
        self.mlx_ptr: ctypes.c_void_p
        self._c_key: Optional[ctypes._CFuncPtr] = None
        self._c_destroy: Optional[ctypes._CFuncPtr] = None

        self._load_mlx_library()
        self._setup_function_prototypes()

        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            raise RuntimeError("Falha ao inicializar MiniLibX.")

    def _load_mlx_library(self) -> None:
        root_dir = Path(__file__).resolve().parent.parent
        so_path = root_dir / "libmlx.so"

        if not so_path.is_file():
            raise ImportError(
                            f"libmlx.so nao encontrada no caminho: {so_path}"
                )

        try:
            self.mlx = ctypes.CDLL(str(so_path))
        except OSError as err:
            raise ImportError(f"Erro ao carregar libmlx.so: {err}")

    def _setup_function_prototypes(self) -> None:
        self.mlx.mlx_init.argtypes = []
        self.mlx.mlx_init.restype = ctypes.c_void_p

        self.mlx.mlx_new_window.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_char_p,
        ]
        self.mlx.mlx_new_window.restype = ctypes.c_void_p

        self.mlx.mlx_new_image.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
        ]
        self.mlx.mlx_new_image.restype = ctypes.c_void_p

        self.mlx.mlx_get_data_addr.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        self.mlx.mlx_get_data_addr.restype = ctypes.c_char_p

        self.mlx.mlx_put_image_to_window.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
        ]
        self.mlx.mlx_put_image_to_window.restype = ctypes.c_int

        self.mlx.mlx_destroy_window.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self.mlx.mlx_destroy_window.restype = ctypes.c_int

        self.mlx.mlx_destroy_image.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self.mlx.mlx_destroy_image.restype = ctypes.c_int

        self.mlx.mlx_key_hook.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self.mlx.mlx_key_hook.restype = ctypes.c_int

        self.mlx.mlx_hook.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self.mlx.mlx_hook.restype = ctypes.c_int

        self.mlx.mlx_loop.argtypes = [ctypes.c_void_p]
        self.mlx.mlx_loop.restype = ctypes.c_int

        self.mlx.mlx_loop_end.argtypes = [ctypes.c_void_p]
        self.mlx.mlx_loop_end.restype = ctypes.c_int

    def _put_pixel_to_buffer(
        self,
        buffer_ptr: BufferPtr,
        line_length: int,
        bpp: int,
        x: int,
        y: int,
        color: int,
    ) -> None:
        if not buffer_ptr:
            return
        bytes_per_pixel = bpp // 8
        offset = (y * line_length) + (x * bytes_per_pixel)
        raw_bytes = bytes([
            color & 0xFF,
            (color >> 8) & 0xFF,
            (color >> 16) & 0xFF,
            0 if bytes_per_pixel == 4 else 0,
        ])
        base_addr = ctypes.cast(buffer_ptr, ctypes.c_void_p).value
        if base_addr is None:
            return
        ctypes.memmove(
            ctypes.c_void_p(base_addr + offset),
            raw_bytes,
            bytes_per_pixel,
        )

    def _draw_rect(
        self,
        buffer_ptr: BufferPtr,
        line_length: int,
        bpp: int,
        sx: int,
        sy: int,
        w: int,
        h: int,
        color: int,
    ) -> None:
        for py in range(sy, sy + h):
            for px in range(sx, sx + w):
                self._put_pixel_to_buffer(
                    buffer_ptr, line_length, bpp, px, py, color
                )

    def _redraw(
        self,
        win_ptr: ctypes.c_void_p,
        maze: Maze,
        path: Optional[List[str]],
    ) -> None:
        wall_c, floor_c, path_c, entry_c, exit_c = self.COLOR_PALETTES[
            self.color_scheme_idx
        ]
        win_w = maze.width * self.cell_size
        win_h = maze.height * self.cell_size

        img_ptr = self.mlx.mlx_new_image(self.mlx_ptr, win_w, win_h)
        if not img_ptr:
            return

        bpp = ctypes.c_int()
        line_length = ctypes.c_int()
        endian = ctypes.c_int()

        buffer_ptr = self.mlx.mlx_get_data_addr(
            img_ptr,
            ctypes.byref(bpp),
            ctypes.byref(line_length),
            ctypes.byref(endian),
        )

        self._draw_rect(
            buffer_ptr,
            line_length.value,
            bpp.value,
            0,
            0,
            win_w,
            win_h,
            floor_c,
        )

        for y in range(maze.height):
            for x in range(maze.width):
                cell: Cell = maze.cell_at(x, y)
                px = x * self.cell_size
                py = y * self.cell_size
                sz = self.cell_size

                if (x, y) == maze.entry:
                    self._draw_rect(
                        buffer_ptr,
                        line_length.value,
                        bpp.value,
                        px,
                        py,
                        sz,
                        sz,
                        entry_c,
                    )
                elif (x, y) == maze.exit:
                    self._draw_rect(
                        buffer_ptr,
                        line_length.value,
                        bpp.value,
                        px,
                        py,
                        sz,
                        sz,
                        exit_c,
                    )

                thick = 2
                if cell.has_wall(Wall.NORTH):
                    self._draw_rect(
                        buffer_ptr,
                        line_length.value,
                        bpp.value,
                        px,
                        py,
                        sz,
                        thick,
                        wall_c,
                    )
                if cell.has_wall(Wall.SOUTH):
                    self._draw_rect(
                        buffer_ptr,
                        line_length.value,
                        bpp.value,
                        px,
                        py + sz - thick,
                        sz,
                        thick,
                        wall_c,
                    )
                if cell.has_wall(Wall.WEST):
                    self._draw_rect(
                        buffer_ptr,
                        line_length.value,
                        bpp.value,
                        px,
                        py,
                        thick,
                        sz,
                        wall_c,
                    )
                if cell.has_wall(Wall.EAST):
                    self._draw_rect(
                        buffer_ptr,
                        line_length.value,
                        bpp.value,
                        px + sz - thick,
                        py,
                        thick,
                        sz,
                        wall_c,
                    )

        if path and self.show_path_flag:
            curr_x, curr_y = maze.entry
            margin = self.cell_size // 4
            size = self.cell_size // 2
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
                    (curr_x, curr_y) != maze.exit
                    and (curr_x, curr_y) != maze.entry
                ):
                    self._draw_rect(
                        buffer_ptr,
                        line_length.value,
                        bpp.value,
                        curr_x * self.cell_size + margin,
                        curr_y * self.cell_size + margin,
                        size,
                        size,
                        path_c,
                    )

        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, win_ptr, img_ptr, 0, 0
        )
        self.mlx.mlx_destroy_image(self.mlx_ptr, img_ptr)

    def render(
        self,
        maze: Maze,
        path: Optional[List[str]] = None,
        color_scheme: int = 0,
    ) -> None:
        _ = color_scheme
        win_w = maze.width * self.cell_size
        win_h = maze.height * self.cell_size

        win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, win_w, win_h, b"A-Maze-ing - MLX Bonus"
        )
        if not win_ptr:
            raise RuntimeError("Falha ao criar janela no MiniLibX.")

        current_maze = maze
        self._redraw(win_ptr, current_maze, path)

        def handle_key(key_code: int, param: ctypes.c_void_p) -> int:
            nonlocal current_maze
            _ = param
            if key_code in (65307, 113):
                self.mlx.mlx_loop_end(self.mlx_ptr)
            elif key_code == 112:
                self.show_path_flag = not self.show_path_flag
                self._redraw(win_ptr, current_maze, path)
            elif key_code == 99:
                self.color_scheme_idx = (
                    self.color_scheme_idx + 1
                ) % len(self.COLOR_PALETTES)
                self._redraw(win_ptr, current_maze, path)
            elif key_code == 114:
                if self.regenerate_callback:
                    current_maze = self.regenerate_callback()
                    self._redraw(win_ptr, current_maze, path)
            return 0

        def handle_destroy(param: ctypes.c_void_p) -> int:
            _ = param
            self.mlx.mlx_loop_end(self.mlx_ptr)
            return 0

        self._c_key = KeyProto(handle_key)
        self._c_destroy = DestroyProto(handle_destroy)

        self.mlx.mlx_key_hook(win_ptr, self._c_key, None)
        self.mlx.mlx_hook(win_ptr, 17, 0, self._c_destroy, None)

        self.mlx.mlx_loop(self.mlx_ptr)
        self.mlx.mlx_destroy_window(self.mlx_ptr, win_ptr)
