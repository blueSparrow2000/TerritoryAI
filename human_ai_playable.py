from environment import *
from agent import Agent

# AI testing ground (ai model inference mode)

endingLoopFrames = FPS*ENDING_DELAY_SECONDS

if __name__ == '__main__':
    global TileMapName, BotList

    # load AI agent
    agent = Agent()
    agent.load_model()

    game = TerritoryGameEnvironment(mapName=TileMapName, bot_infos=BotList)
    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move) # want to execute only ai (use same play step with train step)
        # want to execute with human play

        if done == True:
            game.print_final_scores()
            ######## idle #########
            endingloop = 0
            while endingloop < endingLoopFrames:
                endingloop+=1
                game.idle()
            ######## idle #########
            game.reset()
            # break
    pygame.quit()

