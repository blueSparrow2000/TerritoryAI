import pygame
import numpy as np
from bot import * # this contains Tile
import time
pygame.init()

class TerritoryGameEnvironment:
    def __init__(self, initial_x=1, initial_y=1, trajectoryTrackingMode = False, mapName = 'blank 10 12', bot_infos = [('bot', False),('spiral', False),('spiral', False) ]):
        # UNCHANGED: initialize tile board and display setting
        tileMapData = read_tile_map(mapName)
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

        # init game state - player
        self.player_color = 'dark'  # player color
        self.playerTile = Bot(initial_x, initial_y, self.player_color)
        # set player standing initial tile color
        self.playerTile.setInitialStandingTileColor(self.tiles)
        # self.tiles[initial_y][initial_x].setColor(self.player_color)


        if trajectoryTrackingMode:
            pass
        else:
            # initialize bot players
            bot_colors = Tile.available_colors.copy()
            bot_colors.remove(self.player_color)
            num_other_players = len(bot_infos)
            num_other_players = min(3,num_other_players) # maximum of 3 enemy player
            if num_other_players == 0: # add a spiral if 0 players are given
                num_other_players = 1
                bot_infos = [('spiral', False)]
            start_locations = ((self.col-2, self.row-2), (self.col-2, 1), (1, self.row-2 ))

            self.other_players = [] # assign position and algorithms they use / randomly assign color
            for i in range(num_other_players):
                algo,traceMode = bot_infos[i]
                x_bot,y_bot,color_bot = start_locations[i][0],start_locations[i][1], bot_colors[i]
                bot = None
                if algo == 'spiral':
                    bot = SpiralBot(x_bot, y_bot, color_bot)
                else: # random bot
                    bot = Bot(x_bot, y_bot, color_bot)
                bot.setTraceMode(traceMode)
                bot.setInitialStandingTileColor(self.tiles) # set the initial standing tile color
                self.other_players.append(bot)

            self.entities = [e for e in self.other_players] + [self.playerTile]
            self.all_tile_sprites_list.add(*self.entities)

        self.frame_iteration = 0
        self.max_idle_tolerance = self.total_num_tiles//4  #maximum steps without any obtaining new region

        # some text setting
        self.font_for_score = pygame.font.SysFont('arial', 20)
        self.font_for_winner_message = pygame.font.SysFont('arial', 50, True)
        self.x_winner_message, self.y_winner_message = self.w // 2 - 150, self.h // 2 - 50


        # for trajectory setting (can only store one trajectory to execute)
        self.trajectory = deque([])

    def setTrajectory(self, initial_pos, trajectory):
        self.trajectory = deque(trajectory)

        # pick only one bot to move
        trajectory_bot = SpiralBot(initial_pos[0], initial_pos[1], 'purple' )
        trajectory_bot.setInitialStandingTileColor(self.tiles)  # set the initial standing tile color

        # reset: remove all entities and draw these instead
        self.other_players = [trajectory_bot]
        self.entities = [trajectory_bot]

        self.all_tile_sprites_list.add(*self.entities)

    def reset(self):
        for tile in self.flat_tile_sprites:
            tile.reset()

        for e in self.entities:
            e.reset(self.tiles)

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
        self.clock.tick(FPS)

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
    Only draw sprites
    '''
    def idle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._update_ui_ending()
        self.clock.tick(FPS)

    def simulate_trajectory(self):
        proceed_flag = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # proceed traj
                    proceed_flag = True

        game_over = False
        if not self.trajectory:
            game_over = True
            return game_over, 0

        if proceed_flag:
            # move w.r.t trajectory
            for botE in self.other_players:
                this_direction = Direction(self.trajectory.popleft()) # this is int -> convert to direction
                # print(self.trajectory)
                botE.setDirection(this_direction)
                botE.enforceTarget(self.row, self.col, self.tiles)
                botE.move()
                botE.detect_possible_Enclosure(self.tiles)

        # update with respect to trajectory given
        self._update_ui()
        self.clock.tick(FPS)

        return game_over, 0

    def get_score_sum(self):
        score_sum = 0
        for botE in self.entities:
            score_sum += botE.getScore()
        # print(score_sum)
        return score_sum

    def allTilesOccupied(self):
        return self.get_score_sum() == self.total_num_tiles

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
