import math
import numpy as np
from gym import Env, spaces

from constants import *


class GridWorld(Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, grid_width, grid_height, obstacles=None):
        super(GridWorld, self).__init__()
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = np.zeros((self.grid_height, self.grid_height))
        self.state_space = [i for i in range(self.grid_width * self.grid_height)]
        self.state_space.remove((TARGET_X - 1) + (TARGET_Y - 1) * self.grid_width)
        self.state_space_plus = [i for i in range(self.grid_width * self.grid_height)]
        self.possible_actions = [UP, DOWN, LEFT, RIGHT]
        self.action_result = {
                                UP: - self.grid_width,
                                DOWN: self.grid_width,
                                LEFT: - 1,
                                RIGHT: 1
                              }
        self.action_space = spaces.Discrete(ACTIONS_NUMBER)
        self.observation_space = spaces.Tuple((spaces.Discrete(self.grid_width),
                                               spaces.Discrete(self.grid_height),
                                               spaces.Box(0, DISTANCE_MAX, shape=(1,))))
        # When the obstacles are known
        # if obstacles is not None:
        #     self.obstacles = obstacles
        self.obstacles = []
        self.agent_position = 0
        self.current_distance = 0.0
        self.screen = None

    # X : Row
    # Y : Column
    def get_x_y_from_position(self, position):
        x = position // self.grid_width
        y = position % self.grid_height
        return x, y

    def add_obstacle(self, action, distance):
        obstacle_position = self.agent_position + self.action_result[action]

        if distance < DISTANCE_MAX:
            if obstacle_position not in self.obstacles:
                self.obstacles.append(obstacle_position)
                x, y = self.get_x_y_from_position(obstacle_position)
                self.grid[x][y] = 2

    def is_terminal_state(self, state):
        return state in self.state_space_plus and state not in self.state_space

    def update_agent_position(self, agent_position_state):
        x, y = self.get_x_y_from_position(self.agent_position)
        self.grid[x][y] = 0
        self.agent_position = agent_position_state
        x, y = self.get_x_y_from_position(self.agent_position)
        self.grid[x][y] = 1

    def is_forbidden_move(self, new_state, old_state):
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
        updated_agent_position = self.agent_position + self.action_result[action]
        updated_agent_position_x, updated_agent_position_y = self.get_x_y_from_position(updated_agent_position)

        if self.is_terminal_state(updated_agent_position):
            self.update_agent_position(updated_agent_position)
            reward = 0
            self.current_distance = 0.0
            return np.array((updated_agent_position_x, updated_agent_position_y, self.current_distance)), reward, True, None
        else:
            if not self.is_forbidden_move(updated_agent_position, self.agent_position):
                self.update_agent_position(updated_agent_position)
                self.current_distance = self.euclidean_distance(updated_agent_position_x, updated_agent_position_y, TARGET_X - 1, TARGET_Y - 1)
                reward = - self.current_distance
                return np.array((updated_agent_position_x, updated_agent_position_y, self.current_distance)), reward, False, None
            else:
                old_agent_position_x, old_agent_position_y = self.get_x_y_from_position(self.agent_position)
                self.current_distance = self.euclidean_distance(old_agent_position_x, old_agent_position_y, TARGET_X - 1, TARGET_Y - 1)
                reward = - self.current_distance - 1
                return np.array((old_agent_position_x, old_agent_position_y, self.current_distance)), reward, False, None

    def reset(self):
        self.grid = np.zeros((self.grid_height, self.grid_height))
        self.update_agent_position(0)
        self.grid[TARGET_X - 1][TARGET_Y - 1] = 3
        self.current_distance = 0.0
        x, y = self.get_x_y_from_position(self.agent_position)
        return np.array((x, y, self.current_distance))

    def render(self, mode="human"):
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
        print('----------------------------------------')

    @staticmethod
    def euclidean_distance(x_1, y_1, x_2, y_2):
        return math.sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2)
