import random  # to randomly choose a possible neighbor




NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

ALL_WALLS = NORTH | EAST | SOUTH | WEST
# NORTH 0001, EAST 0010, SOUTH 0100, WEST 1000 --- ALL_WALLS = 1111
# completely closed cell = 15 = 1111

class MazeGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.maze = self.create_maze()
        self.blocked = self.create_42_cells()

    def create_maze(self) -> list[list[int]]:
        maze: list[list[int]] = []

        for y in range(self.height):
            row: list[int] = []

            for x in range(self.width):
                row.append(ALL_WALLS)

            maze.append(row)

        return maze


    def remove_wall(
            self,
            x: int,
            y: int,
            direction: int,
    ) -> None:

        if direction == NORTH:
            self.maze[y][x] &= ~NORTH
            self.maze[y - 1][x] &= ~SOUTH

        elif direction == EAST:
            self.maze[y][x] &= ~EAST
            self.maze[y][x + 1] &= ~WEST

        elif direction == SOUTH:
            self.maze[y][x] &= ~SOUTH
            self.maze[y + 1][x] &= ~NORTH

        elif direction == WEST:
            self.maze[y][x] &= ~WEST
            self.maze[y][x - 1] &= ~EAST


    def get_neighbors(
            self,
            x: int,
            y: int,
            visited: set[tuple[int, int]],
    ) -> list[tuple[int, int, int]]:

        neighbors: list[tuple[int, int, int]] = []

        if x + 1 < self.width and (x + 1, y) not in visited and (x + 1, y) not in self.blocked:
            neighbors.append((x + 1, y, EAST))

        if x - 1 >= 0 and (x - 1, y) not in visited and (x - 1, y) not in self.blocked:
            neighbors.append((x - 1, y, WEST))

        if y + 1 < self.height and (x, y + 1) not in visited and (x, y + 1) not in self.blocked:
            neighbors.append((x, y + 1, SOUTH))

        if y - 1 >= 0 and (x, y - 1) not in visited and (x, y - 1) not in self.blocked:
            neighbors.append((x, y - 1, NORTH))

        return neighbors


    def create_42_cells(
        self,
    ) -> set[tuple[int, int]]:  # use a set for fast membership checks

        pattern_width = 7
        pattern_height = 5

        if self.width < pattern_width + 2 or self.height < pattern_height + 2:
            print("Error: Maze is too small for the 42 pattern.")
            return set()     # return empty set

        pattern_cells: set[tuple[int, int]] = set()

        # 4

        pattern_cells.add((0, 0))
        pattern_cells.add((2, 0))

        pattern_cells.add((0, 1))
        pattern_cells.add((2, 1))

        pattern_cells.add((0, 2))
        pattern_cells.add((1, 2))
        pattern_cells.add((2, 2))

        pattern_cells.add((2, 3))
        pattern_cells.add((2, 4))

        # 2

        pattern_cells.add((4, 0))
        pattern_cells.add((5, 0))

        pattern_cells.add((6, 0))
        pattern_cells.add((6, 1))

        pattern_cells.add((6, 2))
        pattern_cells.add((5, 2))
        pattern_cells.add((4, 2))

        pattern_cells.add((4, 3))
        pattern_cells.add((4, 4))

        pattern_cells.add((5, 4))
        pattern_cells.add((6, 4))

        offset_x = (self.width - pattern_width) // 2
        offset_y = (self.height - pattern_height) // 2

        centered_cells: set[tuple[int, int]] = set()

        for x, y in pattern_cells:
            centered_cells.add((x + offset_x, y + offset_y))

        return centered_cells


    def generate_maze(self) -> list[list[int]]:

        visited: set[tuple[int, int]] = set()

        x = 0
        y = 0

        visited.add((x, y))

        stack: list[tuple[int, int]] = [(x, y)]

        while stack:
            x, y = stack[-1]

            neighbors = self.get_neighbors(
                x,
                y,
                visited,
            )

            if neighbors:
                next_cell = random.choice(neighbors)
                nx, ny, direction = next_cell

                self.remove_wall(x, y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))

            else:
                stack.pop()

        # print("Visited:", len(visited))
        # print("Expected:", width * height - len(blocked))      # Check if the backtracker reached all non-blocked cells

        return self.maze


generator = MazeGenerator(10, 10)
maze = generator.generate_maze()

for row in maze:
    print(row)
