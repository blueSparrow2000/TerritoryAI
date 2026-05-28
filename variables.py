from enum import Enum
from dataclasses import dataclass
from typing import Any
'''
### 실행하기 전에 체크할것:

trajectory 기록하기 모드를 꺼둬야 빠르다
BotList = [('bot', False)]
False 로 해뒀는지 체크!


'''

######## Simulation configuration ##########
@dataclass
class BotInfo:
    type: str = 'bot'
    x: int = -1
    y: int = -1

TileMapName = 'box 20 20'
BotList = [('bot'),('spiral')] #[('bot'),('bot'),('spiral') ] #[('spiral')]  #

#############################################


SIZE = 20 # block pixel size
HALFSIZE = SIZE//2

FPS = 20 # 60 for training
SLOWFPS = 30
ANIMFPS = 20

ENDING_DELAY_SECONDS = 2


# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
SOFTRED = (150, 50, 50)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    def __int__(self):
        return self.value

clock_wise = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT, ]
# print([int(val) for val in clock_wise])
# get 2 orthogonal directions given heading direction
def get_orthogonal_directions(direction):
    idx = clock_wise.index(direction)  # get the index of current direction

    next_idx1 = (idx + 1) % 4
    new_dir1 = clock_wise[next_idx1]  # r -> d -> l -> u

    next_idx2 = (idx - 1) % 4
    new_dir2 = clock_wise[next_idx2]  # r -> u -> l -> d

    return new_dir1,new_dir2

def get_right_orthogonal_directions(direction):
    idx = clock_wise.index(direction)  # get the index of current direction
    next_idx1 = (idx + 1) % 4
    new_dir1 = clock_wise[next_idx1]  # r -> d -> l -> u -> r

    return new_dir1

def get_reverse_direction(direction):
    idx = clock_wise.index(direction)  # get the index of current direction
    reverse_idx = (idx + 2) % 4
    reverse_dir = clock_wise[reverse_idx]  # r -> d -> l -> u -> r

    return reverse_dir

def delta_given_direction(direction):
    dx,dy = 0,0
    if direction == Direction.RIGHT:
        dx += 1
    elif direction == Direction.LEFT:
        dx -= 1
    elif direction == Direction.DOWN:
        dy += 1
    elif direction == Direction.UP:
        dy -= 1
    return dx,dy

# for dir in clock_wise:
#     print(dir)
#     or1, or2 = get_orthogonal_directions(dir)
#     print(or1)
#     print(delta_given_direction(or1))
#     print()
#     print(or2)
#     print(delta_given_direction(or2))
#     print("*"*10)
