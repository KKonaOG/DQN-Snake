# DQN-Snake

This project consists of a terminal-based snake game where two DQN agents progressively learn together.
Feel free to use it as a starting point for any personal projects you would like in the future. All I ask for
is a star if you end up using it <3

Game Mechanics are handled in the `game.py` file.
DQN Agent Mechanics are handled in the `snake.py` file.
The base DQN class is found in the `dqn.py` file.

The `main.py` is the primary control loop file and is where data aggregation and visualization is primarily controlled.
It should be noted that (atleast when writing this), the actual game instance handles drawing the state internally since
it self manages calling the next turn until all snakes are dead. 