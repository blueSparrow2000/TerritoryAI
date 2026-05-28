from environment import *

# copy and paste trajectory value (list of int from 0 to 3 = directions) here
initial_pos = [18,18] # write down color of the bot
traj = read_trajectory_data("trace")

if __name__ == '__main__':
    global TileMapName, BotList
    game = TerritoryGameEnvironment(trajectoryTrackingMode = True, mapName = TileMapName, bot_infos = BotList)
    game.setTrajectory(initial_pos, traj)
    # game loop
    while True:
        game_over, score = game.simulate_trajectory()
        if game_over == True:
            print("Simulation Done!")
            break
    pygame.quit()

