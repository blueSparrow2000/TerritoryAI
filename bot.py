from tile import *
import random

class Bot(Tile):
    nearBy = ((0, -1),(1,0),(0,1),(-1,0))
    clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]

    botID = 0

    def __init__(self, x,y,color, name = None):
        super().__init__(x,y,color)
        self.initial_pos = (x,y)
        self.score = 1

        self.direction = Direction(random.randint(1, 4)) # Direction.RIGHT # 내 마지막 향하는 방향
        self.prev_direction = self.direction
        self.target = None
        self.moveDirectionQueue = deque([]) # 움직일 방향을 저장해두는 queue

        self.image = Tile.head_tile_image_dict[self.color].image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.drawX,self.drawY

        self.traceMode = False
        self.direction_trace = [] # all history of movement directions

        self.trajectory_tracking_mode = False
        self.loaded_trajectory = deque([])
        self.trajectory_direction = None

        self.occupation_stack = []

        self.name = self.color
        if name:
            self.name = name

        self.botID = Bot.botID
        Bot.botID += 1

    ################################## trajectory load stuff #########################
    def load_trajectory(self, traj):
        self.loaded_trajectory = deque(traj)
        self.trajectory_tracking_mode = True

    def reset_trajectory_direction(self):
        self.trajectory_direction = None  # if no op

    def set_forward_trajectory_direction(self, trajectory_index):
        if self.loaded_trajectory[trajectory_index] != 0:  # if it is 0, it is no op
            self.trajectory_direction = Direction(self.loaded_trajectory[trajectory_index])
        else:
            self.trajectory_direction = None # if no op

    def set_reverse_trajectory_direction(self, trajectory_index):
        if self.loaded_trajectory[trajectory_index] != 0:
            self.trajectory_direction = get_reverse_direction(Direction(self.loaded_trajectory[trajectory_index]))  # reverse of the previous move
        else:
            self.trajectory_direction = None # if no op

        # if is_revert:  # revert occupied land... 해당 이동이 occupy하는 이동인지, 원래 내 타일을 이동한거였는지, enclosure했다면 해당 region에 대한 정보 받아와야 함... trajectory진행하면서
        #     # keep track of occupition region / tile that happened in each step, and revert (set color white)
        #     pass

    def free_the_tiles(self, tiles):
        # print("free called: ", self.occupation_stack)
        if len(self.occupation_stack) > 1: # dont take out the very first standing tile
            coordinates = self.occupation_stack.pop()
            target_coords_and_colors = list(map(lambda x:(x[0],x[1],'white'),coordinates))
            Tile.set_colors(tiles, target_coords_and_colors)


    def get_trajectory_direction(self):
        return self.trajectory_direction

    ################################## start saving trajectory #########################
    def setTraceMode(self, traceMode):
        self.traceMode = traceMode

    def reset(self, tiles): # dont change color like super
        # reset position
        self.x,self.y = self.initial_pos
        self.drawX,self.drawY = self.x*SIZE , self.y*SIZE
        self.rect.x, self.rect.y = self.drawX, self.drawY

        # init movement info
        self.direction = Direction.RIGHT
        self.target = None
        self.moveDirectionQueue = deque([])

        # initial position should be occupied
        self.setInitialStandingTileColor(tiles)
        # init score
        self.score = 1

    def write_and_reset_trace(self, fileName):
        # reset trace
        if self.traceMode:
            # 실행 다 끝나고 에러 발견시, 리셋된 다음 시작하려할때 게임 끄면 직전 게임이 저장되어있음. 반드시 리셋 부른 후 꺼야함
            write_trajectory_data(fileName,self.initial_pos, self.color, self.direction_trace)
            # print(self.direction_trace)
            self.direction_trace = []

    def setInitialStandingTileColor(self,tiles):
        tiles[self.y][self.x].setColor(self.color)  # set the initial standing tile color
        self.add_occupation_stack([(self.x, self.y)])

    def getName(self):
        return self.name

    def getScore(self):
        return self.score

    def isTargetValid(self):
        if self.target is None: # no target is assigned
            return False
        targetColor = self.target.getColor()
        if targetColor == 'white' or targetColor == self.color: # can go to my target or empty target
            return True
        return False # color is not white, which means occupied by others

    '''
    Random
    move in a random direction    
    '''
    def setTarget(self,row, col, tiles):
        if self.isTargetValid(): # while valid, dont have to set target
            return
        # choose random target depth 1 (any direction) - clockwise sweep
        my_past_tile = []

        shuffled_random_direction = Bot.clock_wise.copy()
        random.shuffle(shuffled_random_direction)

        for search_direction in shuffled_random_direction:
            dx,dy = delta_given_direction(search_direction)
            xNext,yNext = self.x + dx,self.y + dy
            if (0 <= xNext < col) and (0 <= yNext < row): # valid inside the map
                candidate_target = tiles[yNext][xNext]
                if candidate_target.is_wall():
                    continue
                candidate_target_color = tiles[yNext][xNext].getColor()
                if candidate_target_color == 'white': # successful target
                    self.target = candidate_target
                    self.moveDirectionQueue.append(search_direction)
                    return
                elif candidate_target_color==self.color: # tile i have been to
                    my_past_tile.append((candidate_target, search_direction))

        # no new tile can be reached -> visit my tile // candidate_target_color==self.color
        for past_info in my_past_tile: # go to first one
            self.target = past_info[0]
            self.moveDirectionQueue.append(past_info[1])
            return


    '''
    Enforce target given direction 
    direction이 이미 주어졌다 가정하고 (플레이어나 ai의 경우) 다음 이동할 타겟을 지정하는것 
    '''
    def enforceTarget(self,row,col,tiles):
        # if current move (in direction) is valid (empty tile or my tile) -> move. otherwise, invalid move, dont move
        dx,dy = delta_given_direction(self.direction)
        xNext, yNext = self.x + dx, self.y + dy
        if (0 <= xNext < col) and (0 <= yNext < row): # valid coordinate
            move_to_tile = tiles[yNext][xNext]
            ### 사실 이거 필요 없긴 함 ### 아래에서 self.color 가 'wall'이라서
            if move_to_tile.is_wall():
                return False# invalid move (into the wall)
            ### 사실 이거 필요 없긴 함 ###
            move_tile_color = move_to_tile.getColor()
            if move_tile_color == 'white' or move_tile_color == self.color:  # valid move
                self.target = move_to_tile
                return True # target enforce valid
        return False

    '''
    target으로 가는 방향을 설정 (target이 occupy되지 않은 동안 target으로 가는 경로) 
    target으로 가는 경로는 내 타일 경로임. 그래서 걱정할 필요 없이 가려는 타일이 점령되어 있는지만 보면 됨 
    만약 target이 존재하지 않을때 (adjacent empty tile이 없을때) 종료함
    
    현재 가려는 방향을 리턴... 그 방향대로 움직일거임
    
    나중에 강화학습 시킬때 이게 action임. 이걸로 받아올거야
    '''
    def getAction(self):
        # action queue에서 하나씩 꺼내서 move 함 -> action대로 안되었을때 처리? 흠... 어떻게 하는게 좋으려나
        if self.moveDirectionQueue: # if not empty, get the direction
            self.setDirection(self.moveDirectionQueue.popleft())
        return self.direction

    def setDirection(self, direction):
        self.direction = direction

    '''
    현재 향하려는 방향으로 실제로 한칸 이동. 이때 propagate해야할듯? 
    '''
    def move(self,revert_no_occupation = False):
        occupied_blocks = []
        # no target or already occupied - dont move: wait for assigning the new target
        if not self.isTargetValid():
            # invalid move => append 0
            if self.traceMode: self.direction_trace.append(0)  # save as int format
            if not revert_no_occupation: self.add_occupation_stack(occupied_blocks)
            return

        dx,dy = delta_given_direction(self.direction)
        # move toward the target if tile is empty
        self.moveTile(dx,dy)

        if self.traceMode: self.direction_trace.append(int(self.direction)) # save as int format

        if revert_no_occupation: # dont execute below - just move the head tile
            return

        if self.x == self.target.x and self.y == self.target.y: # arrived on target
            # set color of the current tile to my color
            occupied = self.target.setColor(self.color)

            # add score and reset the target
            self.target = None
            if occupied:
                occupied_blocks.append((self.x, self.y))
                self.score += 1

        self.add_occupation_stack(occupied_blocks)

    def add_occupation_stack(self, coordinates):
        if self.trajectory_tracking_mode:
            self.occupation_stack.append(coordinates)
            # print(self.occupation_stack)

    def append_occupation_stack(self, coordinates):
        if self.trajectory_tracking_mode:
            self.occupation_stack[-1] += coordinates
    '''
    Additional algorithm for enclosure detection
    should be called after move
    '''
    def detect_possible_Enclosure(self, tiles,revert_no_occupation = False):
        if revert_no_occupation: # dont have to check enclosure
            return
        col, row = len(tiles[0]), len(tiles)
        dx,dy = delta_given_direction(self.direction) # direction to find future block (a block that agent will pass if it keeps the direction on the next step)

        xNext,yNext = self.x+dx,self.y+dy

        # highlight front
        # if (0 <= xNext < col) and (0 <= yNext < row) and not tiles[yNext][xNext].is_wall():
        #     tiles[yNext][xNext].turn_highlight_red()

        ortho_dir1, ortho_dir2 = get_orthogonal_directions(self.direction)
        dx1, dy1 = delta_given_direction(ortho_dir1)
        dx2, dy2 = delta_given_direction(ortho_dir2)

        # vertical wall or horizontal wall or self collide -> propagate on two directions!
        if (xNext < 0 or xNext >= col) or (yNext < 0 or yNext >= row) or Tile.is_wall_color(tiles[yNext][xNext].getColor()) or (tiles[yNext][xNext].getColor() == self.color):
            self.call_propagate(tiles,row,col,(self.x + dx1, self.y + dy1))
            self.call_propagate(tiles,row,col,(self.x + dx2, self.y + dy2))
            return

        # for diag check
        xDiag1, yDiag1 = xNext + dx1, yNext + dy1
        xDiag2, yDiag2 = xNext + dx2, yNext + dy2
        # for forward check
        xForward, yForward = xNext + dx, yNext + dy

        # 찾음. 이거 하나라도 해당되면 셋 다 해야하는거임 ㅋㅋㅋㅋ
        # right, left diagonal corner and front - including wall tile is fine 닿여도 되는 부분 리스트임
        if (   (0 <= xDiag1 < col) and (0 <= yDiag1 < row) and (tiles[yDiag1][xDiag1].getColor() == self.color or tiles[yDiag1][xDiag1].is_wall())   ) or  (    (0 <= xDiag2 < col) and (0 <= yDiag2 < row) and (tiles[yDiag2][xDiag2].getColor() == self.color or tiles[yDiag2][xDiag2].is_wall())    ) or (    (0 <= xForward < col) and (0 <= yForward < row) and (tiles[yForward][xForward].getColor() == self.color or tiles[yForward][xForward].is_wall())    ):
            # tiles[yDiag1][xDiag1].turn_highlight_red()
            self.call_propagate(tiles,row,col, (self.x + dx1, self.y + dy1))
            # tiles[yDiag2][xDiag2].turn_highlight_red()
            self.call_propagate(tiles, row, col, (self.x + dx2, self.y + dy2))
            # tiles[yForward][xForward].turn_highlight_red()
            self.call_propagate(tiles, row, col, (self.x + dx, self.y + dy))

    # HELPER: if given position is empty block, call propagate
    def call_propagate(self,tiles,row,col,pos):
        if (0 <= pos[0] < col) and (0 <= pos[1] < row) and tiles[pos[1]][pos[0]].getColor() == 'white':
            self.propagate(tiles, pos)
            # tiles[pos[1]][pos[0]].turn_highlight_red()

    # HELPER: propagate empty tile region and check it is surrounded by my color
    def propagate(self, tiles, seed):
        col, row = len(tiles[0]), len(tiles)
        visited = [[False for c in range(col)] for r in range(row)]
        visited[seed[1]][seed[0]] = True
        queue = deque([seed])
        region = []
        while queue:
            x, y = queue.popleft()
            region.append((x, y, self.color))
            # investigate nearby up, down, left, right nodes
            for dx, dy in Bot.nearBy:
                xNear, yNear = x + dx, y + dy
                if (0 <= xNear < col) and (0 <= yNear < row) and (not visited[yNear][xNear]):  # if inside boundary, check if nearby is occupied by other colors
                    visited[yNear][xNear] = True
                    nearTileColor = tiles[yNear][xNear].getColor()
                    if nearTileColor == self.color or Tile.is_wall_color(nearTileColor):  # same with given color or wall -> pass
                        pass
                    elif nearTileColor == 'white':  # empty cell -> if not visited, put it in queue (put only not visited tiles)
                        queue.append((xNear, yNear))
                    else:  # different color adjacent detected -> quit propagation
                        # print("Not enclosed by one color on (", xNear, ",", yNear, ") :", nearTileColor)
                        return False

        # region is surrounded by only the given color
        Tile.set_colors(tiles, region)
        Tile.set_enclosed(tiles, region) # set enclosed
        # enclosed 그래픽이 문제가 아닌거 같은데 겜이 안끝나
        coordinates = list(map(lambda x:(x[0],x[1]), region))
        self.append_occupation_stack(coordinates)

        enclosed_region_size = len(region)
        self.score += enclosed_region_size
        # print("ENCLOSED REGION SIZE: ",enclosed_region_size)
        return enclosed_region_size  # successfully propagated - return the number of propagated retion which is added to the score



class SpiralBot(Bot):
    def __init__(self, x,y,color, name = None):
        super().__init__(x,y,color,name)

    '''
    Clockwise sweep
    Prioritize searching right side first, then counter clock wise check => overall, the bot moves in clockwise shape
    '''
    def setTarget(self,row, col, tiles):
        if self.isTargetValid(): # while valid, dont have to set target
            return
        # choose random target depth 1 (any direction) - clockwise sweep
        my_past_tile = []
        right_side_direction = get_right_orthogonal_directions(self.direction)
        right_side_direction_index = Bot.clock_wise.index(right_side_direction)

        for i in range(4):
            search_direction_index = (right_side_direction_index-i)%4
            search_direction = Bot.clock_wise[search_direction_index]
            dx,dy = delta_given_direction(search_direction)
            xNext,yNext = self.x + dx,self.y + dy
            if (0 <= xNext < col) and (0 <= yNext < row): # valid inside the map
                candidate_target = tiles[yNext][xNext]
                if candidate_target.is_wall():
                    continue # past tile에도 넣으면 안됨
                candidate_target_color = tiles[yNext][xNext].getColor()
                if candidate_target_color == 'white': # success
                    self.target = candidate_target
                    self.moveDirectionQueue.append(search_direction)
                    return
                elif candidate_target_color==self.color: # tile i have been to
                    my_past_tile.append((candidate_target, search_direction))

        # no new tile can be reached -> visit my tile // candidate_target_color==self.color
        for past_info in my_past_tile: # go to first one
            self.target = past_info[0]
            self.moveDirectionQueue.append(past_info[1])
            return




class GreedyBot(Bot):
    def __init__(self, x,y,color, name = None):
        super().__init__(x,y,color,name)

    '''
    Greedy
    Set target to the nearest empty tile and set the moveDirectionQueue
    
    my self color를 따라가며 가장 처음 발견한 empty tile (white tile)을 target으로 지정 후,
    해당 타일 좌표가 계속 white인 동안 setTarget할 필요 없음 (move를 계속 수행할것임)
    해당 타일 좌표가 나에 의해 또는 다른 플레이어에 의해 점령될 경우 새로운 타겟을 지정하고, 방향큐에 삽입
    
    # 또는 , adjacent tile 을 리스트로 만들어두고 
    처음 4방향 추가해두고(좌표만 저장), 이동 후에 새로운 타일을 adjacent에 추가
    이후 타깃 지정시 occupied 된 타일은 리스트에서 제거하는 방식으로.. stack으로 두면 될듯? 가장 최근 추가한것부터 돌아보는 식
    -> 이렇게 한다면 해당 타일로 가는 경로를 따로 탐색해줘야 함. 
    더 빠르게 경로탐색 - 내가 지나온 타일들 길 위에서만 탐색하면 됨 
    메모리 많이 쓰겠는데...
    '''
    def setTarget(self,row, col, tiles):
        return





















