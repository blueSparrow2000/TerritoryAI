from enum import Enum
from dataclasses import dataclass
from typing import Any




######## Simulation configuration ##########
@dataclass
class BotInfo:
    setTrace: bool = False
    x: int = -1
    y: int = -1

TileMapName = 'box 20 20'
BotList = [('bot', True)]  # [('bot', False),('spiral', False),('spiral', False) ]

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

