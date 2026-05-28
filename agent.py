import torch
import random
import numpy as np
from variables import *
from collections import deque
from environment import TerritoryGameEnvironment
from model import Linear_QNet, QTrainer
from plotting import plot
from tile import Tile

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

'''
AGENT
input 처리
- 나랑 같은 color는 0, white는 1, 다른 color는 -1 으로 인풋 주기
- 지금은 간단하게 3x3 nearby tile정보를 flatten해서 인풋 주기 (벽이 있는 부분은 -1로 받음)

output 처리
- 이걸로 학습. output은 one hot이고, 절대 방향 direction을 argmax해서 얻음

* 지금 direction은 T/F로 처리되어 있음
위치에 대한 정보도 마찬가지로 처리하고 싶은데, 지금 현재 각 위치마다 3가지 상태가 있음
1) 이동할 수 있고, 포인트 주는 white tile
0) 이동할 수 있고, 포인트 안주는 my tile
-1) 이동할 수 없는 상대 tile 또는 벽

이런 상태정보를 주기... 흠 
아니면 각 상태 채널을 3개씩 만들어서 넣어줘야 하나...
생각해보니 방향정보는 필요없음 바로바로 바꿀 수 있음

즉 8개의 nearby window에서 
각각 타일 종류별로 다 나타내볼까? 
벽이랑 적 타일이랑 구분하길 원하면 그것도 따로 해줘야 할듯... enclosure를 효율적으로 만드는거에 필요함. 
벽이랑 내 타일이랑도 다르긴 함. 내 타일은 지나가도 벽은 못지나감

'''
class Agent:
    # window input 들어가는 순서 = 시계방향으로, 위 방향부터
    sensing_window = ((0, -1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)) # 8 including diagonal
    sensing_distance_1_window = ((0, -1),(1,0),(0,1),(-1,0)) # 4
    sensing_distance_2_window = ((0, -1), (0,-2), (1, -1), (1, 0), (2,0), (1, 1), (0, 1), (0,2), (-1, 1), (-1, 0), (-2,0), (-1, -1)) # 12 depth 2 sensing
    # sensing_distance_3_window = (
    # (0, -1), (0, -2), (1, -1), (1, 0), (2, 0), (1, 1), (0, 1), (0, 2), (-1, 1), (-1, 0), (-2, 0), (-1, -1))
    typeOfRegion = ('white', 'my', 'wall', 'enemy') # used for model input size determining
    def __init__(self):
        self.n_games = 0
        self.explore_until_step = 120
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.my_sensing_window = Agent.sensing_distance_2_window
        self.model = Linear_QNet(len(self.my_sensing_window)*len(Agent.typeOfRegion), 256, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        # get states from nearby observation
        nearby_info = []

        col, row = game.col, game.row
        xCenter,yCenter = game.playerTile.getPos()

        # 각 픽셀이 [white인지, 내 땅인지, 벽인지, 적땅인지] 매핑된 정보를 사용

        for dx,dy in self.my_sensing_window:
            xNear, yNear = xCenter + dx, yCenter + dy
            ########################## 그냥 각 정보(벽인지, 내 타일인지, 빈 타일인지, 적 타일인지) 마다 on off 형식으로 줘볼까?
            # region type info: each tile is [isWhite, isMyTile, isWall, isEnemyTile]
            if (0 <= xNear < col) and (0 <= yNear < row):
                this_tile_color = game.tiles[yNear][xNear].getColor()
                if this_tile_color == 'white': # white (empty)
                    nearby_info.append([1,0,0,0])
                elif this_tile_color == game.playerTile.getColor(): # my tile
                    nearby_info.append([0,1,0,0])
                elif Tile.is_wall_color(this_tile_color): # inner wall
                    nearby_info.append([0, 0, 1, 0])
                else:  # other colored tile
                    nearby_info.append([0,0,0,1])
            else: # out of range (wall)
                nearby_info.append([0,0,1,0])

        # transpose the data for locality
        # 1차원으로 평탄화해서 줄때 같은 종류의 픽셀 정보는 비슷한 순서로 들어오게 하려고 함 (몇번째 픽셀인지 정보는 spread out되지만.. 즉 의미적 locality를 원하면 transpose하고, 공간적 locality를 원하면 transpose없이 실행)
        # [ 픽셀1이 white인지, 픽셀 2가 white인지, ... , 픽셀 N이 white인지, 픽셀 1이 내땅인지, ..., 픽셀N이 내땅인지, ... ]
        state = [list(row) for row in zip(*nearby_info)]
        # flatten
        state = [item for sublist in state for item in sublist]

        # print(state)
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, next_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    '''
    Original action - [0,1,0,0] one hot vector
    '''
    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = max(1,self.explore_until_step - self.n_games)
        # max(0,self.explore_until_step - self.n_games)  is same effect as 'self.epsilon = self.explore_until_step - self.n_games'

        final_move = [0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 3)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    global TileMapName, BotList
    plot_scores = []
    plot_mean_scores = deque([])
    total_score = 0
    record = 0
    agent = Agent()
    game = TerritoryGameEnvironment(mapName = TileMapName, bot_infos = BotList)
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()