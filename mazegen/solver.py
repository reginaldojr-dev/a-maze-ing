from collections import deque
from typing import List, Tuple, Dict
from mazegen.maze import Maze
from mazegen.walls import Wall


def solve_bfs(maze: Maze, start: Tuple[int, int], end: Tuple[int, int]) -> List[str]:
    queue = deque([start])
    visited = {start}
    parent: Dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}
    direction_map = {
        Wall.NORTH: (0, -1, "N"),
        Wall.EAST: (1, 0, "E"),
        Wall.SOUTH: (0, 1, "S"),
        Wall.WEST: (-1, 0, "W")
    }
    found = False
    while queue:
        curr = queue.popleft()
        if curr == end:
            found = True
            break
        cx, cy = curr
        cell = maze.cell_at(cx, cy)
        for wall_flag, (dx, dy, dir_char) in direction_map.items():
            if not cell.has_wall(wall_flag):
                nx, ny = cx + dx, cy + dy
                if maze.is_valid_coord(nx, ny) and (nx, ny) not in visited:
                    if not maze.cell_at(nx, ny).is_blocked:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = (curr, dir_char)
                        queue.append((nx, ny))
    if not found:
        return []
    path_dirs = []
    curr = end
    while curr != start:
        prev, direction_char = parent[curr]
        path_dirs.append(direction_char)
        curr = prev
    path_dirs.reverse()
    return path_dirs
