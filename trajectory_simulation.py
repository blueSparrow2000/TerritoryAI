from environment import *

# copy and paste trajectory value (list of int from 0 to 3 = directions) here
initial_pos = [18,18] # write down color of the bot
traj = [2, 3, 2, 2, 4, 2, 2, 3, 2, 4, 2, 3, 2, 4, 2, 3, 3, 2, 3, 3, 1, 1, 4, 4, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 3, 3, 2, 4, 2, 2, 3, 3, 3, 3, 1, 3, 2, 2, 4, 4, 2, 3, 3, 2, 4, 4, 4, 1, 4, 1, 4, 2, 2, 4, 2, 3, 3, 3, 3, 3, 2, 2, 3, 1, 1, 4, 3, 4, 1, 1, 4, 3, 4, 1, 2, 4, 1, 3, 2, 4, 3, 4, 2, 3, 2, 2, 4, 4, 4, 2, 3, 3, 3, 2, 4, 4, 4, 3, 4, 1, 4, 1, 3, 4, 4, 2, 4, 4, 2, 4, 3, 4, 3, 4, 1, 2, 3, 3, 4, 1, 2, 1, 3, 4, 2, 3, 1, 2]


if __name__ == '__main__':
    global TileMapName, BotList
    game = TerritoryGameEnvironment(trajectoryTrackingMode = True, mapName = TileMapName, bot_infos = BotList)
    game.setTrajectory(initial_pos, traj)
    # game loop
    while True:
        game_over, score = game.simulate_trajectory()
        if game_over == True:
            break
    pygame.quit()

