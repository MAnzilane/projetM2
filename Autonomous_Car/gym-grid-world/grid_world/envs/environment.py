import pygame
import numpy as np
from gym import Env, spaces

from lib.hardware.ultrasound import Ultrasound

from constants import *


class GridWorld(Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, grid_width, grid_height, obstacles=None):
        super(GridWorld, self).__init__()
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = np.zeros((self.grid_height, self.grid_height))
        self.state_space = [i for i in range(self.grid_width * self.grid_height)]
        self.state_space.remove(self.grid_width * self.grid_height - 1)
        self.state_space_plus = [i for i in range(self.grid_width * self.grid_height)]
        self.possible_actions = [UP, DOWN, LEFT, RIGHT]
        self.action_result = {
                                UP: -self.grid_width,
                                DOWN: self.grid_height,
                                LEFT: -1,
                                RIGHT: 1
                              }
        self.action_space = spaces.Discrete(ACTIONS_NUMBER)
        self.observation_space = spaces.Tuple((spaces.Discrete(self.grid_width),
                                               spaces.Discrete(self.grid_height)))
                                               # spaces.Box(0, DISTANCE_MAX, shape=(1,))))
        # When the obstacles are known
        # if obstacles is not None:
        #     self.obstacles = obstacles
        self.obstacles = []
        self.agent_position = 0
        self.current_distance = 0
        self.ultrasound = Ultrasound()
        self.screen = None

    def get_x_y_from_position(self, position):
        x = position // self.grid_width
        y = position % self.grid_height
        return x, y

    def add_obstacle(self, obstacle):
        if obstacle not in self.obstacles:
            self.obstacles.append(obstacle)
            # for square in self.obstacles:
            x = obstacle // self.grid_width
            y = obstacle % self.grid_height
            self.grid[x][y] = 2

    def is_terminal_state(self, state):
        return state in self.state_space_plus and state not in self.state_space

    def set_state(self, state):
        # Add distance
        x, y = self.get_x_y_from_position(self.agent_position)
        self.grid[x][y] = 0
        self.agent_position = state
        x, y = self.get_x_y_from_position(self.agent_position)
        self.grid[x][y] = 1

    def off_grid_obstacle_move(self, new_state, old_state):
        if new_state not in self.state_space_plus:
            return True
        elif old_state % self.grid_width == 0 and new_state % self.grid_width == self.grid_width - 1:
            return True
        elif old_state % self.grid_width == self.grid_width - 1 and new_state % self.grid_width == 0:
            return True
        elif new_state in self.obstacles:
            return True
        else:
            return False

    def step(self, action):
        resulting_state = self.agent_position + self.action_result[action]
        resulting_state_x, resulting_state_y = self.get_x_y_from_position(resulting_state)
        # resulting_state_x = resulting_state // self.grid_width
        # resulting_state_y = resulting_state % self.grid_height

        self.current_distance = self.ultrasound.get_distance()
        if self.current_distance < DISTANCE_MAX:
            self.add_obstacle(resulting_state)

        if not self.is_terminal_state(resulting_state):
            reward = -1
        else:
            reward = 0
            self.grid[self.grid_width - 1][self.grid_height - 1] = 1
        if not self.off_grid_obstacle_move(resulting_state, self.agent_position):
            self.set_state(resulting_state)
            # Add distance
            # self.current_distance
            return np.array((resulting_state_x, resulting_state_y)), reward, self.is_terminal_state(self.agent_position), None
        else:
            x, y = self.get_x_y_from_position(self.agent_position)
            # Add distance
            # self.current_distance
            return np.array((x, y)), reward, self.is_terminal_state(self.agent_position), None

    def reset(self):
        self.grid = np.zeros((self.grid_height, self.grid_height))
        self.set_state(0)
        # self.add_obstacles()
        self.grid[self.grid_width - 1][self.grid_height - 1] = 3
        x, y = self.get_x_y_from_position(self.agent_position)
        return np.array((x, y))  # , self.current_distance

    """def render(self, mode="human"):
        print(self.grid)
        print('----------------------------------------')
        for row in self.grid:
            for col in row:
                if col == 0:
                    print('-', end='\t')
                elif col == 1:
                    print('X', end='\t')
                elif col == 2:
                    print('O', end='\t')
            print('\n')
        print('----------------------------------------')"""

    def render(self, mode="human", close=False):
        if close:
            pygame.quit()
        else:
            if self.screen is None:
                pygame.init()
                size = (WINDOW_WIDTH, WINDOW_HEIGHT)
                self.screen = pygame.display.set_mode(size)
                pygame.display.set_caption("My game")

            # Used to manage how fast the screen updates
            clock = pygame.time.Clock()

            # Set the screen background
            self.screen.fill(WHITE)

            # Draw the grid
            for row in range(GRID_ROWS):
                for column in range(GRID_COLUMNS):
                    color = BLACK
                    # Car
                    if self.grid[row][column] == 1:
                        if row == (self.grid_height - 1) and column == (self.grid_width - 1):
                            print("ICI")
                            color = WHITE
                        else:
                            color = BLUE
                    # Obstacle
                    elif self.grid[row][column] == 2:
                        color = RED
                    # Target
                    elif self.grid[row][column] == 3:
                        color = GREEN
                    pygame.draw.rect(self.screen,
                                     color,
                                     [(CELL_MARGIN + CELL_WIDTH) * column + CELL_MARGIN,
                                      (CELL_MARGIN + CELL_HEIGHT) * row + CELL_MARGIN,
                                      CELL_WIDTH,
                                      CELL_HEIGHT])

            clock.tick(350)
            pygame.display.flip()

    @staticmethod
    def move_right(x, y):
        if x + 1 < GRID_COLUMNS:
            return x + 1, y
        return x, y

    @staticmethod
    def move_left(x, y):
        if x - 1 >= 0:
            return x - 1, y
        return x, y

    @staticmethod
    def move_up(x, y):
        if y - 1 >= 0:
            return x, y - 1
        return x, y

    @staticmethod
    def move_down(x, y):
        if y + 1 < GRID_ROWS:
            return x, y + 1
        return x, y
