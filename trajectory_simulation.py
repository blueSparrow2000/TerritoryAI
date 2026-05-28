from environment import *


if __name__ == '__main__':
    global TileMapName, BotList
    game = TerritoryGameEnvironment(trajectoryTrackingFileName = "traceAgent", mapName = TileMapName, bot_infos = BotList)
    # game loop
    while True:
        game_over, score = game.simulate_trajectory()
        if game_over == True:
            print("Simulation Done!")
            break
    pygame.quit()


