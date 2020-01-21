import pygame
import random


def move_right(x, y):
    if x + 1 < GRID_COLUMNS:
        return x + 1, y
    return x, y


def move_left(x, y):
    if x - 1 >= 0:
        return x - 1, y
    return x, y


def move_up(x, y):
    if y - 1 >= 0:
        return x, y - 1
    return x, y


def move_down(x, y):
    if y + 1 < GRID_ROWS:
        return x, y + 1
    return x, y


BLACK = (55, 71, 79)
WHITE = (255, 255, 255)
GREEN = (15, 157, 88)
RED = (219, 68, 55)
BLUE = (66, 133, 244)

GRID_ROWS = 20
GRID_COLUMNS = 20

CELL_WIDTH = 30
CELL_HEIGHT = 30
CELL_MARGIN = 3
WINDOW_WIDTH = GRID_ROWS * (CELL_WIDTH + CELL_MARGIN) + CELL_MARGIN
WINDOW_HEIGHT = GRID_COLUMNS * (CELL_HEIGHT + CELL_MARGIN) + CELL_MARGIN

grid = []
for row in range(GRID_ROWS):
    grid.append([])
    for column in range(GRID_COLUMNS):
        grid[row].append(0)  # Append a cell

# Grid values :
# 1 for car
# 2 for obstacle
# 3 for target
obstacles_positions = [(5, 7), (10, 0), (15, 8), (6, 2), (9, 10)]
for position in obstacles_positions:
    grid[position[0]][position[1]] = 2
car_initial_position = (0, 0)
grid[car_initial_position[0]][car_initial_position[1]] = 1
target_position = (19, 19)
grid[target_position[0]][target_position[1]] = 3

pygame.init()
size = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("My game")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

car_x = 0
car_y = 0
car_last_x = 0
car_last_y = 0
choices = ["up", "down", "right", "left"]
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Set the screen background
    screen.fill(WHITE)

    # Draw the grid
    for row in range(GRID_ROWS):
        for column in range(GRID_COLUMNS):
            color = BLACK
            # Car
            if grid[row][column] == 1:
                color = BLUE
                car_last_x = row
                car_last_y = column
            # Obstacle
            elif grid[row][column] == 2:
                color = RED
            # Target
            elif grid[row][column] == 3:
                color = GREEN
            pygame.draw.rect(screen,
                             color,
                             [(CELL_MARGIN + CELL_WIDTH) * column + CELL_MARGIN,
                              (CELL_MARGIN + CELL_HEIGHT) * row + CELL_MARGIN,
                              CELL_WIDTH,
                              CELL_HEIGHT])

    # Add conditions for obstacles...
    grid[car_last_x][car_last_y] = 0
    choice = random.choices(choices)
    print(choice)
    if choice[0] == "up":
        car_x, car_y = move_up(car_last_x, car_last_y)
    elif choice[0] == "down":
        car_x, car_y = move_down(car_last_x, car_last_y)
    elif choice[0] == "right":
        car_x, car_y = move_right(car_last_x, car_last_y)
    elif choice[0] == "left":
        car_x, car_y = move_left(car_last_x, car_last_y)
    grid[car_x][car_y] = 1

    clock.tick(1)
    pygame.display.flip()

pygame.quit()
