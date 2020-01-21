import numpy as np


class Agent:

    def __init__(self):
        self.states = []
        self.actions = ["up", "down", "left", "right"]
        self.environment = Environment()
        self.learning_rate = 0.2
        self.exploration_rate = 0.3

        # Initial state reward
        self.state_values = {}
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                self.state_values[(i, j)] = 0  # Set initial value to 0

    def choose_action(self):
        # Choose action with most expected value
        max_next_reward = 0
        action = ""

        if np.random.uniform(0, 1) <= self.exploration_rate:
            action = np.random.choice(self.actions)
        else:
            # Greedy action
            for a in self.actions:
                # If the action is deterministic
                next_reward = self.state_values[self.environment.next_state(a)]
                if next_reward >= max_next_reward:
                    action = a
                    max_next_reward = next_reward
        return action

    def take_action(self, action):
        position = self.environment.next_state(action)
        return Environment(state=position)

    def reset(self):
        self.states = []
        self.environment = Environment()

    def play(self, rounds=10):
        i = 0
        while i < rounds:
            # To the end of game back propagate reward
            if self.environment.is_end:
                # Back propagate
                reward = self.environment.get_reward()
                # explicitly assign end state to reward values
                self.state_values[self.environment.state] = reward  # this is optional
                print("Game End Reward", reward)
                for s in reversed(self.states):
                    reward = self.state_values[s] + self.lr * (reward - self.state_values[s])
                    self.state_values[s] = round(reward, 3)
                self.reset()
                i += 1
            else:
                action = self.choose_action()
                # append trace
                self.states.append(self.environment.next_state(action))
                print("current position {} action {}".format(self.environment.state, action))
                # by taking the action, it reaches the next state
                self.environment = self.take_action(action)
                # mark is end
                self.environment.isEndFunc()
                print("nxt state", self.environment.state)
                print("---------------------")

    def show_values(self):
        for i in range(0, BOARD_ROWS):
            print('----------------------------------')
            out = '| '
            for j in range(0, BOARD_COLS):
                out += str(self.state_values[(i, j)]).ljust(6) + ' | '
            print(out)
        print('----------------------------------')


if __name__ == "__main__":
    ag = Agent()
    ag.play(50)
    print(ag.show_values())
