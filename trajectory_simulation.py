from environment import *

if __name__ == '__main__':
    game = TerritoryGameEnvironment(trajectoryTrackingFileName = "traceAgent")
    while True:
        game_over, score = game.simulate_trajectory()
        if game_over == True:
            print("Simulation Done!")
            break
    pygame.quit()


