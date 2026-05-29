# TERRITORY WAR
A python implementation of territory war for Reinforcement Learning




## Installations
This project is based on python. Below are the packages that needs to be installed:

pygame
matplotlib
numpy
pytorch


## Sample run
- Main  menu       

[//]: # (<img src="./sample_run/main.png" width="300" height="300" align="center">  )



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
- dataclass for efficient management


### TODO
- model parameter loading (inference step or learning continously)
- human be able to play with learned model (only inference step)


