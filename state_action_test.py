from environment import *
import torch
from agent import Agent

def translate(type):
    if type == 'blank':
        return [1,0,0]
    elif type == 'myTile':
        return [0,1,0]
    else:
        return [0,0,1]

if __name__ == '__main__':
    # load AI agent - we use same model(agent) for each bots
    agent = Agent()
    agent.load_model() # put a model name here for specific model
    # agent.load_model('model_window2_senseType3') # put a model name here for specific model

    col,row = 10,10
    Agent.set_col_row(col,row)

    # distance 1 window: nearby info has information on [up, right, down, left] order of three-tuple
    # sensing 3 types of cell - white, mytile, obstacle (wall/enemy)

    nearby_infos = [['blank', 'wall', 'wall','wall'],['wall','blank','wall','wall'],['wall','wall','blank','wall'],['wall','wall','wall','blank'],['blank', 'blank', 'blank','blank']]
    states = [] # all kinds of state combinations
    for nearby_info in nearby_infos: # nearby_info = [[1,0,0],[0,0,1],[0,0,1],[0,0,1]]
        nearby_info = list(map(lambda x:translate(x),nearby_info))
        state = nearby_info
        # state = [list(nearby_row) for nearby_row in zip(*nearby_info)] # transpose state
        state = np.array([item for sublist in state for item in sublist], dtype=int) # flatten
        states.append(state)


    for state in states:
        with torch.inference_mode():
            move = agent.get_action_deterministic(state)
            action_as_direction_index = move.index(1)
            direction = clock_wise[action_as_direction_index]
            print("State: {}\nAction: {}\n".format(state, str(direction)))
