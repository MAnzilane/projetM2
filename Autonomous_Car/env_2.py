import matplotlib.pyplot as plt
import numpy as np

# from lib.hardware.ultrasound import Ultrasound

class GridWorld(object):
    def __init__(self, m, n):
        self.grid = np.zeros((m, n))
        self.m = m
        self.n = n
        self.stateSpace = [i for i in range(self.m * self.n)]
        self.stateSpace.remove(self.m * self.n - 1)
        self.stateSpacePlus = [i for i in range(self.m * self.n)]
        self.actionSpace = {'U': -self.m, 'D': self.m,
                            'L': -1, 'R': 1}
        self.possibleActions = ['U', 'D', 'L', 'R']
        self.agentPosition = 0
        self.obstacles = []
        # self.ultrasound = Ultrasound()

    def isTerminalState(self, state):
        return state in self.stateSpacePlus and state not in self.stateSpace

    def getAgentRowAndColumn(self):
        x = self.agentPosition // self.m
        y = self.agentPosition % self.n
        return x, y

    def setState(self, state):
        x, y = self.getAgentRowAndColumn()
        self.grid[x][y] = 0
        self.agentPosition = state
        x, y = self.getAgentRowAndColumn()
        self.grid[x][y] = 1

    def addObstacle(self, obstacle):
        self.obstacles.append(obstacle)
        i = 2
        x = obstacle // self.m
        y = obstacle % self.n
        self.grid[x][y] = i

    def offGridObstacleMove(self, newState, oldState):
        if newState not in self.stateSpacePlus:
            return True
        elif oldState % self.m == 0 and newState % self.m == self.m - 1:
            return True
        elif oldState % self.m == self.m - 1 and newState % self.m == 0:
            return True
        elif newState in self.obstacles:
            return True
        else:
            return False

    def step(self, action):
        x, y = self.getAgentRowAndColumn()
        resultingState = self.agentPosition + self.actionSpace[action]
        # se positionner !
        self.distance = self.ultrasound.get_distance()
        # if self.distance < : # TODO TO DEFINE !
        #     self.addObstacle(resultingState)
        reward = -1 if not self.isTerminalState(resultingState) else 0
        if not self.offGridObstacleMove(resultingState, self.agentPosition):
            self.setState(resultingState)
            # ici on bouge !!!
            return (resultingState,self.distance), reward, self.isTerminalState(self.agentPosition), None

        else:
            return (self.agentPosition,self.distance), reward, self.isTerminalState(self.agentPosition), None

    def reset(self):
        self.agentPosition = 0
        self.grid = np.zeros((self.m, self.n))
        return (self.agentPosition,self.distance)

    def render(self):
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

    def actionSpaceSample(self):
        return np.random.choice(self.possibleActions)


def maxAction(Q, state, actions):
    values = np.array([Q[state[0], a] for a in actions])
    action = np.argmax(values)
    return actions[action]

# Q Learning algorithm by Video on youtube
if __name__ == '__main__':
    # add obstacles !
    #obstacles = [18, 54, 63, 14]
    env = GridWorld(9, 9) #,obstacles)
    # model hyperparameters
    ALPHA = 0.1
    GAMMA = 1.0
    EPS = 1.0

    Q = {}
    for state in env.stateSpacePlus:
        for action in env.possibleActions:
            Q[state, action] = 0

    numGames = 50000
    totalRewards = np.zeros(numGames)
    env.render()
    for i in range(numGames):
        if i % 5000 == 0:
            print('starting game ', i)
        done = False
        epRewards = 0
        observation = env.reset()
        while not done:
            rand = np.random.random()
            action = maxAction(Q, observation, env.possibleActions) if rand < (1 - EPS) \
                else env.actionSpaceSample()
            observation_, reward, done, info = env.step(action)
            epRewards += reward

            action_ = maxAction(Q, observation_, env.possibleActions)
            Q[observation[0], action] = Q[observation[0], action] + ALPHA * (
                        reward + GAMMA * Q[observation_[0], action_] - Q[observation[0], action])
            observation = observation_
        # TODO faut bloquer le robot, le replacer case départ puis relancer !
        if EPS - 2 / numGames > 0:
            EPS -= 2 / numGames
        else:
            EPS = 0
        totalRewards[i] = epRewards

    plt.plot(totalRewards)
    plt.show()
