import pygame
import math
from queue import PriorityQueue

WIDTH = 1200
HEIGHT = 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows, total_columns):
        self.row = row
        self.col = col
        self.width = width
        self.x = col * self.width
        self.y = row * self.width
        self.color = WHITE
        self.total_rows = total_rows
        self.total_columns = total_columns

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  
            self.neighbors.append(grid[self.row - 1][self.col])

        # right
        if self.col < self.total_columns - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)  # manhattan distance formula


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()
            
    return False

#adding spots to to the row and adding rows to the
def make_grid(rows, columns, width, height):
    grid = []
    gap = width // columns
    for i in range(rows):
        grid.append([])
        for j in range(columns):
            spot = Spot(i, j, gap, rows, columns)
            grid[i].append(spot)
    return grid


# def draw_grid(win, rows, columns, width, height):
    # row_gap = height // rows
    # column_gap = width // columns
    # for i in range(rows):
    #     pygame.draw.line(win, GREY, (0, i * row_gap), (width, i * row_gap))
    #     for j in range(columns):
    #         pygame.draw.line(win, GREY, (j * column_gap, 0), (j * column_gap, height))


def draw_barrier(win, grid, rows, columns, total_rows):
    #drawing horizontal barriers
    for row in rows:
        for spot in grid[row]:
            spot.make_barrier()
            spot.draw(win)
    #drawing vertical barriers
    for column in columns:
        for row in range(total_rows):
            spot = grid[row][column]
            spot.make_barrier()
            spot.draw(win)
    
    

def draw(win, grid, rows, columns, width, height):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    pygame.display.update()


def get_clicked_position(pos, rows, columns, width, height):
    gap = width // columns
    x, y = pos
    row = y // gap
    col = x // gap
    return row, col


def main(win, width, height):
    ROWS = 30
    COLUMNUS = 40
    grid = make_grid(ROWS, COLUMNUS ,width, height)

    start = None
    end = None

    run = True
    started = False
    
    barrier_rows = [0,ROWS-1]
    barrier_columns = [0, COLUMNUS-1]
    
    draw_barrier(win, grid, barrier_rows, barrier_columns, ROWS)
    
    ghosts = [grid[5][5], grid[5][9], grid[5][7]]
    
    pacman = grid[8][8]
    
    for ghost in ghosts:
        ghost.make_start()
        print(ghost)
    
    end = pacman
    end.make_end()
    
    while run:
        draw(win, grid, ROWS, COLUMNUS, width, height)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    for ghost in ghosts:
                        algorithm(lambda: draw(win, grid, ROWS, COLUMNUS, width, height),
                                grid, ghost, pacman)

    pygame.quit()


main(WIN, WIDTH, HEIGHT)
