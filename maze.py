import random  # to randomly choose a possible neighbor

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

ALL_WALLS = NORTH | EAST | SOUTH | WEST
# NORTH 0001, EAST 0010, SOUTH 0100, WEST 1000 --- ALL_WALLS = 1111
# completely closed cell = 15 = 1111


def create_maze(width: int, height: int) -> list[list[int]]:

    maze : list[list[int]] = []

    for y in range(height):

        row : list[int] = []

        for x in range(width):
            row.append(ALL_WALLS)

        maze.append(row)

    return maze


def remove_wall(
        maze: list[list[int]],
        x: int,
        y: int,
        direction: int,
) -> None:

    if direction == NORTH:
        maze[y][x] &= ~NORTH
        maze[y - 1][x] &= ~SOUTH
        
    elif direction == EAST:
        maze[y][x] &= ~EAST
        maze[y][x + 1] &= ~WEST

    elif direction == SOUTH:
        maze[y][x] &= ~SOUTH
        maze[y + 1][x] &= ~NORTH

    elif direction == WEST:
        maze[y][x] &= ~WEST
        maze[y][x - 1] &= ~EAST



def get_neighbors(
        x: int,
        y: int,
        width: int,
        height: int,
        visited: set[tuple[int, int]],
        blocked: set[tuple[int, int]],
) -> list[tuple[int, int, int]]:

    neighbors: list[tuple[int, int, int]] = []

    if x + 1 < width and (x + 1, y) not in visited and (x + 1, y) not in blocked:
        neighbors.append((x + 1, y, EAST))

    if x - 1 >= 0 and (x - 1, y) not in visited and (x - 1, y) not in blocked:
        neighbors.append((x - 1, y, WEST))

    if y + 1 < height and (x, y + 1) not in visited and (x, y + 1) not in blocked:
        neighbors.append((x, y + 1, SOUTH))

    if y - 1 >= 0 and (x, y - 1) not in visited and (x, y - 1) not in blocked:
        neighbors.append((x, y - 1, NORTH))

    return neighbors


def create_42_cells(
        width: int,
        height: int,
) -> set[tuple[int, int]]: # use a set for fast membership checks

    pattern_width = 7
    pattern_height = 5

    if width < pattern_width + 2 or height < pattern_height + 2:
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

    offset_x = (width - pattern_width) // 2
    offset_y = (height - pattern_height) // 2

    centered_cells: set[tuple[int, int]] = set()

    for x, y in pattern_cells:
        centered_cells.add((x + offset_x, y + offset_y))

    return centered_cells



def generate_maze(
        width: int,
        height: int,
) -> list[list[int]]:

    maze = create_maze(width, height)

    blocked = create_42_cells(width, height)

    visited: set[tuple[int, int]] = set()

    x = 0
    y = 0

    visited.add((x, y))

    stack: list[tuple[int, int]] = [(x, y)]

    while stack:
        x, y = stack[-1]

        neighbors = get_neighbors(
            x,
            y,
            width,
            height,
            visited,
            blocked
        )

        if neighbors:
            next_cell = random.choice(neighbors)
            nx, ny, direction = next_cell

            remove_wall(maze, x, y, direction)
            visited.add((nx, ny))
            stack.append((nx, ny))

        else:
            stack.pop()

    # print("Visited:", len(visited))
    # print("Expected:", width * height - len(blocked))      # Check if the backtracker reached all non-blocked cells

    return maze


maze = generate_maze(10, 10)

for row in maze:
    print(row)

