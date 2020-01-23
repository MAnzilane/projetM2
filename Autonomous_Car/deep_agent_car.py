import gym
import grid_world_car
import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from collections import deque

from control_car import *
from constants import *


class Agent:
    def __init__(self, environment):
        self.discount_factor = DISCOUNT_FACTOR
        self.exploration_rate = INITIAL_EXPLORATION_RATE
        self.exploration_rate_min = EXPLORATION_RATE_MIN
        self.exploration_rate_decay = EXPLORATION_RATE_DECAY
        self.learning_rate = LEARNING_RATE
        self.tau = TAU
        self.batch_size = BATCH_SIZE

        self.environment = environment
        self.memory = deque(maxlen=2000)

        self.model = self.create_model()
        self.target_model = self.create_model()

    def choose_action(self, state):
        self.exploration_rate *= self.exploration_rate_decay
        self.exploration_rate = max(self.exploration_rate_min, self.exploration_rate)
        if np.random.random() < self.exploration_rate:
            return self.environment.action_space.sample()
        return np.argmax(self.model.predict(state, verbose=0)[0])

    def add_to_memory(self, state, action, reward, new_state, done):
        self.memory.append([state, action, reward, new_state, done])

    def create_model(self):
        model = Sequential()
        # state_shape = self.environment.observation_space.shape
        model.add(Dense(24, input_dim=STATE_SHAPE, activation="relu"))
        model.add(Dense(48, activation="relu"))
        model.add(Dense(24, activation="relu"))
        model.add(Dense(self.environment.action_space.n))
        model.compile(loss="mean_squared_error",
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def model_train(self):
        if len(self.memory) < self.batch_size:
            return
        samples = random.sample(self.memory, self.batch_size)
        for sample in samples:
            state, action, reward, new_state, done = sample
            target = self.target_model.predict(state)
            # End of episode (Terminal state)
            if done:
                target[0][action] = reward
            else:
                q_future = max(self.target_model.predict(new_state)[0])
                target[0][action] = reward + q_future * self.discount_factor
            self.model.fit(state, target, epochs=1, verbose=0)

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def save_model(self, filename):
        self.model.save(filename)


def main():
    environment = gym.make('Grid-World-Car-v0', grid_width=GRID_COLUMNS, grid_height=GRID_ROWS, obstacles=[5, 10, 18])
    environment = environment.unwrapped

    episodes = 10
    episode_length = 100
    agent = Agent(environment=environment)
    
    for trial in range(episodes):
        # Initial state of the trial
        print("Episode {}".format(trial))
        #
        current_state = environment.reset().reshape(1, STATE_SHAPE)
        environment.render()
        for step in range(episode_length):
            print("Step {}".format(step))
            # environment.render()
            action = agent.choose_action(current_state)
            distance = update_position(action)
            environment.add_obstacle(action, distance)
            new_state, reward, done, info = environment.step(action)
            print("Current", current_state, "New", new_state)
            # if (int(current_state[0]) != int(new_state[0])) or (int(current_state[1]) != int(new_state[1]))
            # if not np.array_equal(current_state[:2], new_state[:2]):
            x_1 = current_state[0]
            x_2 = new_state[0]
            y_1 = current_state[1]
            y_2 = new_state[1]
            if (int(x_1) != int(x_2)) or (int(y_1) != int(y_2)):
                forward()
            new_state = new_state.reshape(1, STATE_SHAPE)
            agent.add_to_memory(current_state, action, reward, new_state, done)
            agent.model_train()  # Internally iterates default (prediction) model
            agent.target_train()  # Iterates target model

            current_state = new_state
            if done:
                break
        stop()
        enter = input("Press \'Enter\' to continue")
        if enter == "":
            continue

    environment.close()
    stop()


if __name__ == "__main__":
    main()
