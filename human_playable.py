from environment import *

endingLoopFrames = FPS*ENDING_DELAY_SECONDS

if __name__ == '__main__':
    global TileMapName, BotList
    # trajectory save mode : trajectorySaveFileName = "trace" 이거 None으로 바꿔줘야 trace없는 더 빠른 모드임
    # game = TerritoryGameEnvironment(trajectorySaveFileName = "trace", mapName = TileMapName, bot_infos = BotList)

    # without trajectory save
    game = TerritoryGameEnvironment( mapName=TileMapName, bot_infos=BotList)
    # game loop
    while True:
        game_over = game.play_step_human_playable()
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

