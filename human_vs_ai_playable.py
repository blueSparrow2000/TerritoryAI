from environment import *
from agent import Agent

# AI testing ground (ai model inference mode)

endingLoopFrames = FPS*ENDING_DELAY_SECONDS

if __name__ == '__main__':
    global TileMapName, BotList

    # load AI agent - we use same model(agent) for each bots
    agent = Agent()
    agent.load_model() # put a model name here for specific model

    game = TerritoryGameEnvironment(mapName=TileMapName, bot_infos=BotList)
    while True:
        states = [agent.get_state(ai_bot, game.tiles) for ai_bot in game.ai_players]
        moves = [agent.get_action_deterministic(state) for state in states]

        # perform move and get new state
        game_over, score = game.play_step_human_playable(moves)
        if game_over == True:
            game.print_final_scores()
            ######## idle #########
            endingloop = 0
            while endingloop < endingLoopFrames:
                endingloop += 1
                game.idle()
            ######## idle #########
            game.reset()
    pygame.quit()

