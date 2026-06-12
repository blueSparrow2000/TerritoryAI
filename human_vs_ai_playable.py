from environment import *
import torch
from agent import Agent

# AI testing ground (ai model inference mode)

endingLoopFrames = FPS*ENDING_DELAY_SECONDS

if __name__ == '__main__':
    global TileMapName, BotList
    # TileMapName = 'blank 20 20'  # 'circle 15' #'blank 20 20'
    # BotList = (BotInfo('bot'),)
    
    # load AI agent - we use same model(agent) for each bots
    agent = Agent()
    # agent.load_model()
    agent.load_model('DQN_window2_senseType3') # put a model name here for specific model

    # if you only want bots and algorithms
    # no_player = True,
    game = TerritoryGameEnvironment(record_mode=True,mapName=TileMapName, bot_infos=BotList)
    col,row = game.get_col_row_info()
    Agent.set_col_row(col,row) # ai agent의 row col 세팅 해줘야 함
    while True:
        states = [agent.get_state(ai_bot, game.tiles) for ai_bot in game.ai_players]

        with torch.inference_mode():
            # moves = [agent.get_action(state) for state in states]
            moves = [agent.get_action_deterministic(state) for state in states]
            # moves = [agent.get_action(state) for state in states]

        # perform move and get new state
        game_over = game.play_step_human_playable(moves)
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

