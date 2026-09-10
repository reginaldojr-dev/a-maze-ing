from mazegen.walls import Wall


class Cell:
	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y
		self. walls = Wall.ALL
		self.is_blocked = False

	def remove_wall(self, wall: Wall) -> None:
		self.walls &= ~wall

	def add_wall(self, wall: Wall) -> None:
		self.walls |= wall

	def has_wall(self, wall: Wall) -> bool:
		return bool(self.walls & wall)

	def wall_count(self) -> int:
		count = 0
		w = int(self.walls)
		while w > 0:
			count += w & 1
			w >>= 1
		return count
