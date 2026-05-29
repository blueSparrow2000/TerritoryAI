'''
Enclosure

given
1) list of blocks on the board
2) starting points (seed: 0~2 points=coordinates)
3) color to check enclosure

check whether a region is enclosed or not
if enclosed, change all block color in the area as given color

https://stackoverflow.com/questions/10856634/pygame-blitting-only-updated-surfaces

https://devnauts.tistory.com/63


이제 가뒀을때 영역 먹히는게 구현이 됨

1) 랜덤 움직임 및 갈 수 있는곳 찾는 길찾기 코드 (dumb ai) agent 만들기
2) territoryAI 시뮬레이터 만들어서 돌릴 수 있게 만들기 (보상 등)
3) clockwise sweep 같은 유명한 알고리즘 agent도 구현해두기
4) 강화학습 돌릴 수 있게 input output 정의: 현재 상황인 tile map 상황을 줘서 학습? (2D array를 통째로 줄까) / output은 상하좌우 방향 원핫 벡터
5) 모델 파라미터 저장해두고 불러오기 기능 찾고 구현 (ai 써서 기능 구현해도 될듯)
'''

import pygame
from tile import *
pygame.init()

def posToScreen(pos):
    column, row = pos
    return column * SIZE, row * SIZE
def screenToPos(pos):
    column, row = pos
    return column / SIZE, row / SIZE

##### INITIALIZE MAP #####
# read tilemap and get the values
tileMapData = read_tile_map('test 1')
col,row = len(tileMapData[0]), len(tileMapData)

WIDTH, HEIGHT = col*SIZE,row*SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TerritoryWar")

tiles,num_occupiable_tiles = Tile.generate_tile_map(tileMapData)
# Text로부터 생성하지 않을시
# tiles = [[Tile(c,r) for c in range(col)] for r in range(row)]
# set the initial tile color (x,y,color)
# tile_color_list = [(0,0,'red'),(0,1,'red'), (1,0,'red'),(2,0,'red'), (0,2,'red'),(1,2,'red'),(2,1,'red') ]
# Tile.set_colors(tiles,tile_color_list)

##### INITIALIZE MAP #####


'''
# Enclosure Detection call 
when to call propagate function on which seed

Given
1) my color
2) my current position
3) my direction that I moved to get to current position

Does
Detect whether to call propagate function or not 
If called, determine seeds and call propagate

Return
None
'''
# helper function: if given position is empty block, call propagate
def call_propagate(tiles,given_color,pos):
    if tiles[pos[1]][pos[0]].getColor() == 'white':
        propagate(tiles, given_color, pos)

def detect_possible_Enclosure(tiles, given_color, pos, direction):
    col, row = len(tiles[0]), len(tiles)
    dx,dy = delta_given_direction(direction) # direction to find future block (a block that agent will pass if it keeps the direction on the next step)
    x,y = pos
    xNext,yNext = x+dx,y+dy

    future_tile = tiles[yNext][xNext]

    ortho_dir1, ortho_dir2 = get_orthogonal_directions(direction)
    dx1, dy1 = delta_given_direction(ortho_dir1)
    dx2, dy2 = delta_given_direction(ortho_dir2)

    if (not (0 <= xNext < col)) or (not (0 <= yNext < row)) or (future_tile.getColor() == given_color) : # vertical wall or horizontal wall or self collide -> propagate on two directions!
        call_propagate(tiles, given_color,(x + dx1, y + dy1))
        call_propagate(tiles, given_color,(x + dx2, y + dy2))
        return

    future_tile_side1 = tiles[yNext+dy1][xNext+dx1]
    future_tile_side2 = tiles[yNext+dy2][xNext+dx2]

    if future_tile_side1.getColor() == given_color:
        call_propagate(tiles, given_color, (x + dx1, y + dy1))

    if future_tile_side2.getColor() == given_color:
        call_propagate(tiles, given_color, (x + dx2, y + dy2))



'''
# BFS search the list of tiles
col -> x
row -> y
grid is same as tile position

(x,y) = tiles[y][x] 

for each seed, run 'propagate'

First tile (seed) must be empty tile (= white tile = unoccupied)

# if found other color adjacent tile, return immediately in the BFS loop (return false and do nothing)
# 벽에 닿은건 따로 처리해줄 필요 없음. 그냥 블럭이 옆에 없는거 처리가 됨, 우리가 찾는건 empty cell 연결된 것중에서 다른 색깔의 것과 닿았는지만 보면 됨
# else, if closure by only one color (and possibly with wall), set color of all blocks that are visited(put them into separate list to keep track) to given_color
'''
# seed 는 가장 마지막으로 추가된 블럭의 양 옆을 쓰면 됨. 가장 마지막으로 추가된 블럭이 내 색깔 블럭과 인접했을때, 또는 벽에 닿았을때(boundary condition) propagate가 발동함. 주변의 모든 empty cell 에 대해 발동하는데, seed는 0~2개임

def propagate(tiles, given_color,seed):
    print('propagate called!')
    nearBy = ((1, 0), (-1, 0), (0, 1), (0, -1))
    col, row = len(tiles[0]), len(tiles)
    visited = [[False for c in range(col)] for r in range(row)]
    queue = deque([seed])
    region = []
    while queue:
        x,y = queue.popleft()
        region.append((x,y,given_color))
        visited[y][x] = True
        # investigate nearby up, down, left, right nodes
        for dx,dy in nearBy:
            xNear, yNear = x+dx, y+dy
            if (0 <= xNear < col) and (0 <= yNear < row): # if inside boundary, check if nearby is occupied by other colors
                nearTileColor = tiles[yNear][xNear].getColor()
                if nearTileColor == given_color: # same with given color -> pass
                    pass
                elif nearTileColor == 'white': # empty cell -> if not visited, put it in queue (put only not visited tiles)
                    if not visited[yNear][xNear]:
                        queue.append((xNear, yNear))
                else: # different color adjacent detected -> quit propagation
                    print("Not enclosed by one color on (", xNear,",", yNear,") :", nearTileColor)
                    return False

    # region is surrounded by only the given color
    Tile.set_colors(tiles, region)
    return True # successfully propagated



'''
Test
'''
SURFACE_COLOR = (0,0,0)

all_sprites_list = pygame.sprite.RenderPlain() # pygame.sprite.Group()
# object_ = Tile(10,10,'red')
# all_sprites_list.add(object_)
all_sprites_list.add(*tiles)

exit_game = True
clock = pygame.time.Clock()

i=0
while exit_game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game = False

    all_sprites_list.update()
    screen.fill(SURFACE_COLOR)
    all_sprites_list.draw(screen)
    pygame.display.flip()
    # for sp in all_sprites_list:
    #     sp.move(1,0)
    if i == 2:
        # print(propagate(tiles, 'red', (2, 1)))  # 변화 있어야
        # detect_possible_Enclosure(tiles, 'red', (1,0), Direction.UP) # test detect 1
        # detect_possible_Enclosure(tiles, 'red', (2, 2), Direction.RIGHT) # test detect 2
        detect_possible_Enclosure(tiles, 'red', (3, 3), Direction.RIGHT)  # test detect 3

    i+=1
    clock.tick(FPS)


pygame.quit()














