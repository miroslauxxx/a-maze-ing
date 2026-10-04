import random  # to randomly choose a possible neighbor
import sys


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

ALL_WALLS = NORTH | EAST | SOUTH | WEST
# NORTH 0001, EAST 0010, SOUTH 0100, WEST 1000 --- ALL_WALLS = 1111
# completely closed cell = 15 = 1111

class MazeGenerator:
    def __init__(self, width: int, height: int, perfect: bool, seed: int, entry: tuple[int, int], exit: tuple[int, int]) -> None:
        self.width = width
        self.height = height
        self.perfect = perfect
        self.seed = seed
        self.entry = entry
        self.exit = exit

        random.seed(self.seed)

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


    def count_walls(self, x: int, y:int) -> int:
        count = 0
        if self.maze[y][x] & NORTH:
            count += 1
        if self.maze[y][x] & EAST:
            count += 1
        if self.maze[y][x] & SOUTH:
            count += 1
        if self.maze[y][x] & WEST:
            count += 1
        return count
    

    def add_loops(self) -> None:
        dead_ends = []
        opened_walls = 0
        
        for y in range(self.height):
            for x in range(self.width):

                if (
                    self.count_walls(x, y) == 3
                    and (x, y) not in self.blocked
                ):
                    dead_ends.append((x, y)) # tuple appenden

        for x, y in dead_ends:

            if self.count_walls(x, y) != 3:
                continue                   
            # Diese (x, y)-Zelle nicht weiter bearbeiten. Nimm die nächste aus dead_ends
            
            candidates = []

            if (
                self.maze[y][x] & EAST 
                and x + 1 < self.width 
                and (x + 1, y) not in self.blocked
            ):
                candidates.append(EAST)
            if (
                self.maze[y][x] & NORTH 
                and y - 1 >= 0
                and (x, y - 1) not in self.blocked
            ):
                candidates.append(NORTH)
            if (
                self.maze[y][x] & WEST
                and x - 1 >= 0 
                and (x - 1, y) not in self.blocked
            ):
                candidates.append(WEST)
            if (
                self.maze[y][x] & SOUTH
                and y + 1 < self.height
                and (x, y + 1) not in self.blocked
            ):
                candidates.append(SOUTH)


            if candidates:
                random.shuffle(candidates)

                for direction in candidates:
                    if not self.would_create_open_3x3(x, y, direction):
                        self.remove_wall(x, y, direction)
                        opened_walls += 1
                        # break wenn eine Richtg. gefunden
                        # die kein 3x3 öffnet
                        break


        print ("Additional walls opened:", opened_walls)
    

    def open_corners(self) -> None:

            corners = [
                (0, 0),
                (self.width - 1, 0),
                (0, self.height - 1),
                (self.width - 1, self.height - 1)
            ]

            for x, y in corners:

                if x == 0:
                    self.remove_wall(x, y, EAST)

                elif x == self.width - 1:
                    self.remove_wall(x, y, WEST)

                if y == 0:
                    self.remove_wall(x, y, SOUTH)

                elif y == self.height - 1:
                    self.remove_wall(x, y, NORTH)

    def open_center(self) -> None:
        offset_x = (self.width - 7) // 2
        offset_y = (self.height - 5) // 2
        center_x = offset_x + 3
        center_y = offset_y + 2

        print("Center:", center_x, center_y)

        self.remove_wall(center_x, center_y, NORTH)
        self.remove_wall(center_x, center_y, SOUTH)


    def is_open_3x3(self, start_x: int, start_y: int) -> bool:
    # check horizontal connections
        for y in range(start_y, start_y + 3):
            for x in range(start_x, start_x + 2):
                if self.maze[y][x] & EAST:
                    return False
    # check vertical connections
        for x in range(start_x, start_x + 3):
            for y in range(start_y, start_y + 2):
                if self.maze[y][x] & SOUTH:
                    return False

        return True

    def add_wall(self, x: int, y: int, direction: int) -> None:
        if direction == NORTH:
            self.maze[y][x] |= NORTH
            self.maze[y - 1][x] |= SOUTH
    
        elif direction == EAST:
            # | setzt das EAST-Bit auf 1, 
            # während alle anderen Bits ihren Wert behalten
            self.maze[y][x] |= EAST
            self.maze[y][x + 1] |= WEST

        elif direction == SOUTH:
            self.maze[y][x] |= SOUTH
            self.maze[y + 1][x] |= NORTH

        elif direction == WEST:
            self.maze[y][x] |= WEST
            self.maze[y][x - 1] |= EAST


    def would_create_open_3x3(
            self,
            x: int,
            y: int,
            direction: int
    ) -> bool:
        # Wand nur zum Testen öffnen
        self.remove_wall(x, y, direction)

        # Jeden 3x3-Block prüfen, der ins Maze passt
        for start_y in range(self.height - 2):
            for start_x in range(self.width - 2):

                # Verbotenes offenes 3x3 gefunden?
                if self.is_open_3x3(start_x, start_y):
                    # dann Test rückgängig machen, wand wieder zu
                    self.add_wall(x, y, direction)
                    return True

        self.add_wall(x, y, direction)
        return False


    

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


    def is_valid_entry_or_exit(self, position: tuple[int, int]) -> bool:
        x, y = position

        if (
            0 <= x < self.width
            and 0 <= y < self.height
            and position not in self.blocked
        ):
            return True

        return False

    def check_entry_exit(self) -> bool:
        if (
            self.is_valid_entry_or_exit(self.entry)
            and self.is_valid_entry_or_exit(self.exit)
            and self.entry != self.exit
        ):
            return True

        return False

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
        # print("Expected:", self.width * self.height - len(self.blocked))      # Check if the backtracker reached all non-blocked cells
        
        if not self.perfect:
            self.add_loops()
            self.open_corners()
            self.open_center()

        return self.maze

    def check_connectivity(self) -> bool:
        visited = set()
        stack = [(0, 0)]
        visited.add((0, 0))

        while stack:
            x, y = stack.pop()

            # EAST
            if (
                x + 1 < self.width
                and not (self.maze[y][x] & EAST)
                and (x + 1, y) not in visited
            ):
                visited.add((x + 1, y))
                stack.append((x + 1, y))

            # WEST
            if (
                x - 1 >= 0
                and not (self.maze[y][x] & WEST)
                and (x - 1, y) not in visited
            ):
                visited.add((x - 1, y))
                stack.append((x - 1, y))

            # SOUTH
            if (
                y + 1 < self.height
                and not (self.maze[y][x] & SOUTH)
                and (x, y + 1) not in visited
            ):
                visited.add((x, y + 1))
                stack.append((x, y + 1))

            # NORTH
            if (
                y - 1 >= 0
                and not (self.maze[y][x] & NORTH)
                and (x, y - 1) not in visited
            ):
                visited.add((x, y - 1))
                stack.append((x, y - 1))

        expected = self.width * self.height - len(self.blocked)

        print("Visited:", len(visited))
        print("Expected:", expected)

        return len(visited) == expected


    def count_dead_ends(self) -> int:
        dead_ends = 0

        for y in range(self.height):
            for x in range(self.width):
                if (
                    (x, y) not in self.blocked
                    and self.count_walls(x, y) == 3
                ):
                    dead_ends += 1
                    print("Dead end at:", x, y)

        return dead_ends


    def check_borders(self) -> bool:
        # Oben und unten
        for x in range(self.width):
            if not (self.maze[0][x] & NORTH):
                print("Open border: NORTH at", x, 0)
                return False

            if not (self.maze[self.height - 1][x] & SOUTH):
                print("Open border: SOUTH at", x, self.height - 1)
                return False

        # Links und rechts
        for y in range(self.height):
            if not (self.maze[y][0] & WEST):
                print("Open border: WEST at", 0, y)
                return False

            if not (self.maze[y][self.width - 1] & EAST):
                print("Open border: EAST at", self.width - 1, y)
                return False

        print("Borders are valid")
        return True


    def check_wall_coherence(self) -> bool:
        for y in range(self.height):
            for x in range(self.width):
                # EAST prüfen
                if x + 1 < self.width:
                    if (
                        bool(self.maze[y][x] & EAST)
                        != bool(self.maze[y][x + 1] & WEST)
                    ):
                        return False
                
                # SOUTH prüfen
                if y + 1 < self.height:
                    if (
                        bool(self.maze[y][x] & SOUTH)
                        != bool(self.maze[y + 1][x] & NORTH)
                    ):
                        return False
                    
        return True
    

    def check_no_loops(self) -> bool:
        visited = set()
        stack = [((0, 0), None)]

        while stack:
            (x, y), parent = stack.pop()

            if (x, y) in visited:
                continue

            visited.add((x, y))

            neighbors = []

            # NORTH offen?
            if y > 0 and not (self.maze[y][x] & NORTH):
                neighbors.append((x, y - 1))

            # EAST offen?
            if x + 1 < self.width and not (self.maze[y][x] & EAST):
                neighbors.append((x + 1, y))

            # SOUTH offen?
            if y + 1 < self.height and not (self.maze[y][x] & SOUTH):
                neighbors.append((x, y + 1))

            # WEST offen?
            if x > 0 and not (self.maze[y][x] & WEST):
                neighbors.append((x - 1, y))

            for neighbor in neighbors:

                if neighbor == parent:
                    continue

                if neighbor in visited:
                    return False

                stack.append((neighbor, (x, y)))

        return True


    

seed = 42

entry = (0, 0)
exit = (9, 9)

generator = MazeGenerator(10, 10, True, seed, entry, exit)

if not generator.check_entry_exit():  # Wenn Entry/Exit ungültig sind
    print("Error: Invalid entry or exit.")
    sys.exit(1)  # Programm wurde wegen eines Fehlers beendet

print("Perfect:", generator.perfect)
print("Entry/Exit valid:", generator.check_entry_exit())


maze = generator.generate_maze()

print("No loops:", generator.check_no_loops())

print("Wall coherence:", generator.check_wall_coherence())

print("Connected:", generator.check_connectivity())
generator.check_borders()

# fertiges Maze auf offene 3x3-Bereiche prüfen
for start_y in range(generator.height - 2):
    for start_x in range(generator.width - 2):
        if generator.is_open_3x3(start_x, start_y):
            print("OPEN 3x3 FOUND:", start_x, start_y)

print("Dead ends:", generator.count_dead_ends())

for row in maze:
    print(row)
