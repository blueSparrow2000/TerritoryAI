import pygame
import numpy as np
from bot import * # this contains Tile
import time
pygame.init()

class TerritoryGameEnvironment:
    def __init__(self, trajectorySaveFileName = None,trajectoryTrackingFileName = None, mapName = 'blank 10 12', bot_infos = (BotInfo('spiral'),)):
        self.trajectorySaveFileName = trajectorySaveFileName
        self.trajectoryTrackingFileName = trajectoryTrackingFileName

        self.mapName = mapName
        trajectory_data = None # only used in trajectory simulation
        if self.trajectoryTrackingFileName:
            trajectory_data = read_trajectory_data(self.trajectoryTrackingFileName)
            self.mapName = trajectory_data[0] # change map name

        # UNCHANGED: initialize tile board and display setting
        tileMapData = read_tile_map(self.mapName)

        self.col, self.row = len(tileMapData[0]), len(tileMapData)
        WIDTH, HEIGHT = self.col * SIZE, self.row * SIZE
        self.w = WIDTH
        self.h = HEIGHT

        # UNCHANGED: init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("TerritoryWar")
        self.clock = pygame.time.Clock()
        # UNCHANGED: set tilemap
        self.tiles,num_occupiable_tiles = Tile.generate_tile_map(tileMapData)
        self.total_num_tiles = num_occupiable_tiles
        self.all_tile_sprites_list = pygame.sprite.RenderPlain()
        self.flat_tile_sprites = [j for sub in self.tiles for j in sub]
        self.all_tile_sprites_list.add(*self.flat_tile_sprites)

        # if circle, start_locations = ((self.col-8, self.row-8), (self.col-8, 6), (6, self.row-8 ))
        wall_dist = 1
        if mapName.startswith('circle'):
            _, radius = mapName.split(' ')
            radius = int(radius)
            wall_dist = radius//2 - 1
        start_locations = ((wall_dist,wall_dist), (self.col - (wall_dist+1), self.row - (wall_dist+1)), (self.col - (wall_dist+1), wall_dist), (wall_dist, self.row - (wall_dist+1)))

        # init game state - player
        self.player_color = 'dark'  # player color
        player_location = start_locations[0]
        self.playerTile = Bot(player_location[0], player_location[1], self.player_color)
        # set player standing initial tile color
        self.playerTile.setInitialStandingTileColor(self.tiles)

        self.other_players = []
        self.entities = []

        self.trajectory_length = 0
        if self.trajectoryTrackingFileName:
            print("Trajectory Tracking Mode: Press Enter or Right arrow key to proceed")
            trajectory_data = trajectory_data[1:]

            for bot_traj_data in trajectory_data:
                botX, botY = bot_traj_data[0], bot_traj_data[1]
                botColor = bot_traj_data[2]
                botTraj = bot_traj_data[3]

                bot = Bot(botX, botY, botColor)
                self.trajectory_length = len(botTraj) # 한번만 세팅해주면 되는데 여러번 세팅하고있음 (많아야 봇 개수만큼, 어차피 다 같을것)
                bot.load_trajectory(botTraj)

                bot.setInitialStandingTileColor(self.tiles)  # set the initial standing tile color

                self.other_players.append(bot)

            self.entities = self.other_players # same as other players list

        else:
            # initialize bot players
            bot_colors = Tile.available_colors.copy()
            bot_colors.remove(self.player_color)
            num_other_players = len(bot_infos)
            num_other_players = min(3,num_other_players) # maximum of 3 enemy player
            if num_other_players == 0: # add a spiral if 0 players are given
                num_other_players = 1
                bot_infos = (BotInfo('spiral'),)



            self.other_players = [] # assign position and algorithms they use / randomly assign color
            for i in range(num_other_players):
                this_bot_info = bot_infos[i]

                if this_bot_info.custom_coord: bot_start_location = this_bot_info.custom_coord
                else: bot_start_location = start_locations[i+1]
                if this_bot_info.color: this_bot_color = this_bot_info.color
                else: this_bot_color = bot_colors[i]

                x_bot,y_bot,color_bot = bot_start_location[0],bot_start_location[1], this_bot_color

                bot = None
                if this_bot_info.type == 'spiral':
                    bot = SpiralBot(x_bot, y_bot, color_bot)
                else: # random bot
                    bot = Bot(x_bot, y_bot, color_bot)
                bot.setInitialStandingTileColor(self.tiles) # set the initial standing tile color
                self.other_players.append(bot)

            self.entities = [e for e in self.other_players] + [self.playerTile]

            # additional mode check - just set bit
            if self.trajectorySaveFileName:
                print("Trajectory save mode: Trajectory right before the 'reset' will be saved")
                for botE in self.entities:
                    botE.setTraceMode(True)

        self.all_tile_sprites_list.add(*self.entities)

        self.frame_iteration = 0
        self.max_idle_tolerance = self.row+self.col  #maximum steps without any obtaining new region

        # some text setting
        self.font_for_score = pygame.font.SysFont('arial', 20)
        self.font_for_winner_message = pygame.font.SysFont('arial', 50, True)
        self.x_winner_message, self.y_winner_message = self.w // 2 - 150, self.h // 2 - 50

        # for trajectory setting (can only store one trajectory to execute)
        # 이 두 값은 모든 봇이 동일하게 움직임
        self.trajectory_index = 0


    def reset(self):
        for tile in self.flat_tile_sprites:
            tile.reset()

        # save trajectory mode 처리

        # initialize trajectory file that will be saved
        if self.trajectorySaveFileName:
            init_trajectory_data(self.trajectorySaveFileName, self.mapName) # we use append mode for writtng, so we initialize it with write mode writting empty string

        for e in self.entities:
            e.reset(self.tiles)
            if self.trajectorySaveFileName:
                e.write_and_reset_trace(self.trajectorySaveFileName)

        self.frame_iteration = 0

    def collect_decision_and_move(self):
        self.playerTile.enforceTarget(self.row, self.col, self.tiles)
        # 1-2. collect bot decisions
        for botE in self.other_players:
            botE.setTarget(self.row, self.col, self.tiles)  # input to botE
            botE.getAction()  # get output from botE

        # 2. move
        self.playerTile.move()  # player move
        self.playerTile.detect_possible_Enclosure(self.tiles)  # score 합이 120 안되는듯?
        for botE in self.other_players:  # botE move
            botE.move()
            botE.detect_possible_Enclosure(self.tiles)

    '''
    Train agent loop
    '''
    def play_step(self,action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # get action from AI, which is a direction input
        previous_score = self.playerTile.getScore()
        previous_sum_score = self.get_score_sum()
        '''
        We need direction as output, so we only need index (direction)     
        '''
        action_as_direction_index = action.index(1)
        direction = clock_wise[action_as_direction_index]  # action is defined by clock wise directions
        self.playerTile.setDirection(direction) # player는 타겟을 안정하고, 방향을 먼저 정한다

        # 2
        self.collect_decision_and_move()
        # assign reward after enclosure
        score_after_action = self.playerTile.getScore()
        after_action_sum_score = self.get_score_sum()

        reward = score_after_action - previous_score
        amount_of_tiles_somebody_occupied = after_action_sum_score - previous_sum_score
        if amount_of_tiles_somebody_occupied > 0: # gained some region - reset counter
            self.frame_iteration = 0

        # 3. update ui and clock
        self._update_ui()
        self.clock.tick(TRAINFPS)

        # 4. check if over (all tiles are occupied)
        game_over = False
        if self.allTilesOccupied() or self.frame_iteration > self.max_idle_tolerance: # al region occupied or nothing happened for too long
            game_over = True
            self.sort_score()  # sort the scores
            return reward, game_over, self.playerTile.getScore()

        # 5. return game over and score
        return reward, game_over, self.playerTile.getScore()


    def play_step_human_playable(self):
        # 1-1. collect user input : player는 타겟을 정하지 않고, 방향을 먼저 정한다
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.playerTile.setDirection(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.playerTile.setDirection(Direction.RIGHT)
                elif event.key == pygame.K_UP:
                    self.playerTile.setDirection(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.playerTile.setDirection(Direction.DOWN)
                elif event.key == pygame.K_r:
                    self.reset()
        # 2
        self.collect_decision_and_move()

        # 3. update ui and clock
        self._update_ui()
        self.clock.tick(FPS)

        # 4. check if over (all tiles are occupied)
        game_over = False
        if self.allTilesOccupied():
            game_over = True
            self.sort_score() # sort the scores
            return game_over, self.playerTile.getScore()

        # 5. return game over and score
        return game_over, self.playerTile.getScore()

    '''
    Only draw sprites (at the end of human play game)
    '''
    def idle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._update_ui_ending()
        self.clock.tick(FPS)

    '''
    Trajectory
    '''
    def reset_trajectory_directions(self):
        for botE in self.entities:
            botE.reset_trajectory_direction()

    def proceed_trajectory(self):
        self.reset_trajectory_directions()
        if self.trajectory_index < self.trajectory_length: # not reached end
            for botE in self.entities:
                botE.set_forward_trajectory_direction(self.trajectory_index)

            self.trajectory_index += 1  # set next direction index to execute

    def revert_trajectory(self):
        self.reset_trajectory_directions()
        if self.trajectory_index > 0:  # not reached start
            self.trajectory_index -= 1 # decrement first

            for botE in self.entities:
                botE.set_reverse_trajectory_direction(self.trajectory_index)


    def simulate_trajectory(self):
        execute_trajectory = False
        revert_no_occupation = False
        # for faster trajectory
        keys = pygame.key.get_pressed()  # 꾹 누르고 있으면 계속 실행되는 것들
        if keys[pygame.K_RETURN]:
            execute_trajectory = True
            self.proceed_trajectory()
        if keys[pygame.K_BACKSPACE]:
            execute_trajectory = True
            revert_no_occupation = True
            self.revert_trajectory()

        # for faster trajectory
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT: # proceed traj
                    execute_trajectory = True
                    self.proceed_trajectory()
                elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_LEFT: # GO BACK TRAJECTORY
                    execute_trajectory = True
                    revert_no_occupation = True
                    self.revert_trajectory()

        game_over = False
        # if :
        #     game_over = True
        #     return game_over, 0

        ## 아직 revert 했을때 region occupy한거 되돌리는거는 안함. enclosure를 되돌려야 하는 문제가 있다 ㅠㅠ
        if execute_trajectory:
            # move w.r.t trajectory
            for botE in self.entities:
                this_direction = botE.get_trajectory_direction()
                if this_direction:
                    # free the tiles should be called only on revert
                    if revert_no_occupation:
                        botE.free_the_tiles(self.tiles)
                    botE.setDirection(this_direction)
                    botE.enforceTarget(self.row, self.col, self.tiles)
                    # botE.move()
                    # botE.detect_possible_Enclosure(self.tiles)
                    botE.move(revert_no_occupation)
                    botE.detect_possible_Enclosure(self.tiles,revert_no_occupation)


        # update with respect to trajectory given
        self._update_ui()
        self.clock.tick(FPS)

        return game_over, 0

    def _update_ui(self):
        # draw the head of the tile last -> so that it is on top

        self.all_tile_sprites_list.update()
        self.display.fill(WHITE)
        self.all_tile_sprites_list.draw(self.display)

        text = self.font_for_score.render("Score: " + str(self.playerTile.getScore()), True, RED)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _update_ui_ending(self):
        # draw the head of the tile last -> so that it is on top

        self.all_tile_sprites_list.update()
        self.display.fill(WHITE)
        self.all_tile_sprites_list.draw(self.display)

        text = self.font_for_score.render("Score: " + str(self.playerTile.getScore()), True, RED)
        self.display.blit(text, [0, 0])

        text = self.font_for_winner_message.render("Winner is " + self.get_winner_color(), True, SOFTRED)
        self.display.blit(text, [self.x_winner_message, self.y_winner_message])

        pygame.display.flip()

    '''
    score 
    '''
    def get_score_sum(self):
        score_sum = 0
        for botE in self.entities:
            score_sum += botE.getScore()
        # print(score_sum)
        return score_sum

    def allTilesOccupied(self):
        return self.get_score_sum() == self.total_num_tiles

    def sort_score(self):
        self.entities.sort(key = lambda e:-e.getScore())

    def get_winner_color(self):
        winner_color = self.entities[0].getColor()
        if winner_color == 'dark':
            winner_color = 'player'
        return winner_color

    def print_final_scores(self):
        print("All region aquired!")
        print("#" * 10, " Final Score ", "#" * 10)
        score_tuple_list = [(botE.getColor(), botE.getScore()) for botE in self.entities]
        for score_tuple in score_tuple_list:
            entity_name = score_tuple[0]
            if entity_name == 'dark': # player
                entity_name = 'player'
            print("{:10s} : {:5d}".format(entity_name,score_tuple[1]))

        print("{:8s} {} / {}".format('Sum',self.get_score_sum(),self.total_num_tiles))
