from environment import *

endingLoopFrames = FPS*ENDING_DELAY_SECONDS

if __name__ == '__main__':
    global TileMapName, BotList
    game = TerritoryGameEnvironment(mapName = TileMapName, bot_infos = BotList)
    # game loop
    while True:
        game_over, score = game.play_step_human_playable()
        if game_over == True:
            game.print_final_scores()
            ######## idle #########
            endingloop = 0
            while endingloop < endingLoopFrames:
                endingloop+=1
                game.idle()
            ######## idle #########
            game.reset()
            # pygame.time.delay(ENDING_DELAY_SECONDS * 1000)  # 1 sec delay
            # break # if you only want one game
    pygame.quit()

