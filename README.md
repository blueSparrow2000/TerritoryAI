# TERRITORY WAR
A python implementation of territory war for Reinforcement Learning


Change the variables in 'variables.py' to try out different tilemaps & bots


## Installations
This project is based on python. Below are the packages that needs to be installed:

pygame
matplotlib
numpy
pytorch


## Run
Run 'agent.py' to train RL agent

Run 'human_playable.py' to play yourself 

Use Arrow keys to move to each direction

For both case, player and agents are 'black' colored, and other colors are bots



To record the trace of the run, set the trajectorySaveFileName = "[trace file name]" parameter in the environment initialization

Then, the most recent run before the game reset will be recorded into [trace file name].txt file in 'trajectoryData' folder(make sure you close the run after reset - for manual reset, press 'R', then exit the pygame)

Run 'trajectory_simulation.py' with trajectoryTrackingFileName = "[trace file name]" parameter set

Press Enter for forward step, Backspace for backward step

## Sample run
- Main  menu       

<img src="./sample_run/sample_run.png" width="300" align="center">

### maps
- blank (10 x 12)

<img src="./sample_run/map_blank_10_12.png" width="100" align="center">

- box (20 x 20)

<img src="./sample_run/map_box_20_20.png" width="200" align="center">

- circle (radius 10)

<img src="./sample_run/map_circle_10.png" width="200" align="center">


- maze (TBU)




### Youtube test link 


## Files
- tile.py      
Tile class
- bot.py      
Bot class - player, bots, ai all uses this class, which moves 
- agent.py       
trainable Agent class
- model.py      
Agent model NN
- environment.py          
Environment for learning
- human_playable.py      
Interactable game (without AI)
- trajectory_simulation.py
Execute trajectory saved as txt file
- enclosureProblem.py      
Enclosing algorithm
- container.py      
Image, Text class
- gui.py      
GUI (UNUSED)
- plotting.py      
for plotting graph
- tileDataIO.py      
read & write .txt files
- variables.py      
contains global variables



## Version history
2026.05.27 Initial commit               
2026.05.28 Git Reset             
- Added trajectory simulation (Enter to forward, Backspace to reverse - step by step using Right/Left arrow keys)      
- Enclosure bug fixed 

2026.05.29 
- plotting recent 10 scores           
- blank map and circle maps of any size can be generated!
- dataclass for better bot list

- model parameter loading (for inference or continued learning)

2026.06.01
- human be able to play with learned model (only inference step)

2026.06.02
- ai model not working properly (only stays the same place) 

2026.06.12
- make method to check all (current state -> action) pairs 
- bug fix (Agent map, col information must be set manually at the beginning!)



# AI info
The agent retrieves state information about tiles that are closer than 2 units (window distance 2).            
Tile information is classified into the following three types:          

White tile (Score +1 when moving)          

My tile (Score +0 when moving)          

Enemy tile or wall (Score -1 when moving;moving in that direction is canceled and becomes a meaningless move)          
           
The agent can take actions to move one pixel up, down, left, or right using the above state information.           

The reward is +1 when capturing one white tile, +2 when capturing more than one white tile, -1 when attempting to move to a wall or opponent's tile, and 0 otherwise (moving to already visited tile).           

Behavior: 

I trained the agent against a random algorithm in a 20x20 box, and the agent dug a long path to lure the random algorithm into a trap, making it take a long time to escape! 
I hadn't thought of such a strategy.


# Discussion
2026.06.02
생각해보니 이 게임은 내 주변이 이런 상태일때 반드시 한 방향으로만 가야 보상이 최대가 되고 그런게 아님
환경에 non stationarity? 가 있는듯. 
즉 벽에 부딫히는 경우 방향을 틀어야 한다 와 같은 기본적인걸 먼저 배우고 나서 상호작용을 배워야 할수도 있다
그리고, 보상이 크게 + 가 되는 경우가 있으니, 흰 타일로 이동하는걸 0, 내 자신 타일 이동하거나 벽으로 이동해 막히는 경우 보상 -1 로 하면
좀 더 벽이나 내가 지나갔던 경로를 회피할지도? 문제는 deterministic하게 하면 아예 내가 지나갔던 경로를 지나가지 않게됨 
POMDP라서 발생하는 문제. 같은 상황으로 보여도, 더 보상 많이 받는 움직임이 그때그때 다를 수 있으면 stochacity를 유지해야 할까?          

결론: 이동 불가시 보상 -1 

