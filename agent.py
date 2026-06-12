import torch
import random
import numpy as np
import os
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
### 실행하기 전에 체크할 것:
trajectory 기록하기 모드를 꺼둬야 빠르다
'''

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

* 보상이 문제인가? 빈칸으로 이동하기만 하면 +1 주고, 내 타일이나 아무곳도 이동안되면 +0 (벽이나 상대에게 막히는 등)
previous action정보를 주는게 맞는듯 하다
[ up down left right ]
해서 previous action이 각 방향중 어느 방향이었는지를 주기 
(첫 방향은 기본적으로 RIGHT로 가게 설정되어있어서, 처음 움직임 direction은 리플레이 버퍼에서 제거해야 할듯... 아닌가 모든 주변타일 공백인 채로 시작하면 오른쪽으로 가게하는거라.. 괜찮나)

-> 과거 방향을 인풋으로 주는건 별로인듯. 직전의 방향전환한 방향 이런 정보 아니면 딱히. snake 처럼 움직여야



[할거] 
Model check point만들어서 이어서 학습할 수 있도록 만들기\
https://medium.com/analytics-vidhya/saving-and-loading-your-model-to-resume-training-in-pytorch-cb687352fa61
'''

class Agent:
    # window input 들어가는 순서 = 시계방향으로, 위 방향부터
    sensing_window = ((0, -1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)) # 8 including diagonal
    sensing_distance_1_window = ((0, -1),(1,0),(0,1),(-1,0)) # 4
    sensing_distance_2_window = ((0, -1), (0,-2), (1, -1), (1, 0), (2,0), (1, 1), (0, 1), (0,2), (-1, 1), (-1, 0), (-2,0), (-1, -1)) # 12 depth 2 sensing
    sensing_distance_3_window = ((0, -1), (0, -2),(0,-3), (1,0), (2,0), (3,0), (0,1), (0,2), (0,3), (-1,0), (-2,0), (-3,0), (1,-1), (1,-2), (2,-1),(1,1),(2,1),(1,2),(-1,1), (-2,1), (-1,2), (-1,-1), (-1,-2), (-2,-1) )
    # typeOfRegion = ('white', 'my', 'wall', 'enemy')#('white', 'my', 'wall', 'enemy') # used for model input size determining
    typeOfRegion = ('blank', 'me', 'obstacle') # obstacle is wall or enemy
    agentID = 0

    # map helper variables - need to be set
    mapCol, mapRow = 0, 0

    def __init__(self):
        self.n_games = 0
        self.explore_until_step = 120
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.my_sensing_window = Agent.sensing_distance_2_window
        self.model = Linear_QNet(len(self.my_sensing_window)*len(Agent.typeOfRegion), 256, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

        self.agentID = Agent.agentID
        Agent.agentID += 1

    def load_model(self, modelName='model0'): # model0.pth
        modelName += '.pth'
        model_folder_path = self.model.get_model_folder_path()
        file_name = os.path.join(model_folder_path, modelName)
        self.model.load_state_dict(torch.load(file_name))
        # self.model.eval()


    def get_state(self, bot, tiles):
        # print("Feeding state of ",bot.botID)
        # get states from nearby observation
        nearby_info = []

        xCenter,yCenter = bot.getPos()
        agent_color = bot.getColor()


        # 각 픽셀이 [white인지, 내 땅인지, 벽인지, 적땅인지] 매핑된 정보를 사용
        if len(Agent.typeOfRegion) == 4:
            for dx,dy in self.my_sensing_window:
                xNear, yNear = xCenter + dx, yCenter + dy
                ########################## 그냥 각 정보(벽인지, 내 타일인지, 빈 타일인지, 적 타일인지) 마다 on off 형식으로 줘볼까?
                # region type info: each tile is [isWhite, isMyTile, isWall, isEnemyTile]
                if (0 <= xNear < Agent.mapCol) and (0 <= yNear < Agent.mapRow):
                    this_tile_color = tiles[yNear][xNear].getColor()
                    if this_tile_color == 'white': # white (empty)
                        nearby_info.append([1,0,0,0])
                    elif this_tile_color == agent_color: # my tile
                        nearby_info.append([0,1,0,0])
                    elif Tile.is_wall_color(this_tile_color): # inner wall
                        nearby_info.append([0, 0, 1, 0])
                    else:  # other colored tile
                        nearby_info.append([0,0,0,1])
                else: # out of range (wall)
                    nearby_info.append([0,0,1,0])

        elif len(Agent.typeOfRegion) ==3: # cell into 3 type
            for dx,dy in self.my_sensing_window:
                xNear, yNear = xCenter + dx, yCenter + dy
                ########################## 그냥 각 정보(벽인지, 내 타일인지, 빈 타일인지, 적 타일인지) 마다 on off 형식으로 줘볼까?
                # region type info: each tile is [isWhite, isMyTile, isObstacle] # Obstacle = not movable
                if (0 <= xNear < Agent.mapCol) and (0 <= yNear < Agent.mapRow):
                    this_tile_color = tiles[yNear][xNear].getColor()
                    if this_tile_color == 'white': # white (empty)
                        nearby_info.append([1,0,0])
                    elif this_tile_color == agent_color: # my tile
                        nearby_info.append([0,1,0])
                    else:  # other colored tile or wall
                        nearby_info.append([0,0,1])
                else: # out of range (wall)
                    nearby_info.append([0,0,1])

        # transpose the data for locality
        # 1차원으로 평탄화해서 줄때 같은 종류의 픽셀 정보는 비슷한 순서로 들어오게 하려고 함 (몇번째 픽셀인지 정보는 spread out되지만.. 즉 의미적 locality를 원하면 transpose하고, 공간적 locality를 원하면 transpose없이 실행)
        # [ 픽셀1이 white인지, 픽셀 2가 white인지, ... , 픽셀 N이 white인지, 픽셀 1이 내땅인지, ..., 픽셀N이 내땅인지, ... ]

        # state를 transpose해서 줄지 그냥 줄지
        # state = [list(nearby_row) for nearby_row in zip(*nearby_info)]
        state = nearby_info

        state = [item for sublist in state for item in sublist] # flatten

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
        self.epsilon = self.explore_until_step - self.n_games
        #self.epsilon = max(1,self.explore_until_step - self.n_games)
        # max(0,self.explore_until_step - self.n_games)  is same effect as 'self.epsilon = self.explore_until_step - self.n_games'

        final_move = [0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon: # epsilon greedy
            move = random.randint(0, 3)
            final_move[move] = 1
            return final_move
        # choose greedy action
        return self.get_action_deterministic(state)

    # choose greedy action
    def get_action_deterministic(self, state):
        final_move = [0, 0, 0, 0]
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)
        # print(prediction)
        move = torch.argmax(prediction).item()
        final_move[move] = 1

        return final_move

    @classmethod
    def set_col_row(cls, col, row):
        cls.mapCol = col
        cls.mapRow = row

def train():
    # global TileMapName, BotList
    TileMapName = 'blank 20 20'  # 'circle 15' #'blank 20 20'
    BotList = (BotInfo('bot'),)

    # plot helper: for keeping recent 10 scores
    last_N_games = 10
    oldest_index = 0
    last_N_scores = []

    # points for plotting
    plot_scores = []
    plot_mean_scores = [] # mean of last 10 scores will be appended here

    record = 0
    agent = Agent()
    # trace mode
    # game = TerritoryGameEnvironment(trajectorySaveFileName = "traceAgent",mapName = TileMapName, bot_infos = BotList)
    # without trace
    game = TerritoryGameEnvironment(mapName=TileMapName, bot_infos=BotList)
    col,row = game.get_col_row_info()
    Agent.set_col_row(col,row)
    while True:
        # get old state
        state_old = agent.get_state(game.controllable_bot_list[0], game.tiles)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game.controllable_bot_list[0], game.tiles)

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
                agent.model.save() # 기록 갱신하는 모델 파라미터는 저장됨
                print("** Model saved! **")

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            mean_score = 0
            if len(last_N_scores) < last_N_games:
                last_N_scores.append(score)
                mean_score = sum(last_N_scores) / len(last_N_scores)
            else:
                last_N_scores[oldest_index] = score
                oldest_index = (oldest_index+1)%last_N_games
                mean_score = sum(last_N_scores) / last_N_games

            plot_scores.append(score)  # plot each score points at each iteration
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()