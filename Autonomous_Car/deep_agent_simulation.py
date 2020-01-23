import gym
import time
import grid_world_simulation
import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from collections import deque

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
    environment = gym.make('Grid-World-Simulation-v0', grid_width=GRID_COLUMNS, grid_height=GRID_ROWS, obstacles=[])

    episodes = 10
    episode_length = 100
    agent = Agent(environment=environment)
    
    for trial in range(episodes):
        # Initial state of the trial
        print("Episode {}".format(trial))
        current_state = environment.reset()
        reshaped_current_state = current_state.reshape(1, STATE_SHAPE)
        for step in range(episode_length):
            print("Step {}".format(step))
            environment.render()
            action = agent.choose_action(reshaped_current_state)
            print("Action", action)
            new_state, reward, done, info = environment.step(action)
            print("Current", reshaped_current_state, "New", new_state)

            new_state = new_state.reshape(1, STATE_SHAPE)
            agent.add_to_memory(reshaped_current_state, action, reward, new_state, done)

            agent.model_train()  # Internally iterates default (prediction) model
            agent.target_train()  # Iterates target model

            reshaped_current_state = new_state
            if done or step == episode_length - 1:
                environment.render()
            if done:
                time.sleep(1)
                break
    environment.close()


if __name__ == "__main__":
    main()
