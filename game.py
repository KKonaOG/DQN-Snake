import numpy as np
from snake import Snake
from os import system, name
import copy
import time

# Utilitiy Function
# Found at: https://www.geeksforgeeks.org/clear-screen-python/
def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

class Game():
    MINIMUM_FOOD = 3
    NUMBER_SNAKES = 2
    SIMULATION_SPEED = 0.05
    
    def __init__(self) -> None:    
        self.game_number = 0  
        self.turn = 1
        self.game_ended = False
        self.board_matrix = np.zeros((11, 11), dtype=int)
        self.snakes = []
        self.food_locations = []
    
    def resetGame(self):
        # This resets the game for the next round
        self.game_number += 1
        self.turn = 0
        self.spawnSnakes()
        self.spawnFood(self.MINIMUM_FOOD)
        self.updateState()
    
    def nextTurn(self) -> bool:
        self.turn += 1
        
        # Rewards for Each Snake
        rewards = [0 for _ in range(len(self.snakes))]
        
        # Get the Snake Moves
        for snake in self.snakes:
            # Dead snakes are not polled
            if (not snake.alive):
                continue
            
            action = snake.getMove()
            
            # Update Snake Head Position
            if (action == "UP"):
                snake.head[0] -= 1
            elif (action == "DOWN"):
                snake.head[0] += 1
            elif (action == "LEFT"):
                snake.head[1] -= 1
            elif (action == "RIGHT"):
                snake.head[1] += 1
            else:
                continue
            
            snake.body.append(copy.copy(snake.head))
        
            # This is a self collision check. It needs to
            # be here since the body is updated below
            if (snake.head in snake.body[:-1]):
                snake.alive = False
                continue
        
            if snake.head in self.food_locations:
                self.food_locations.remove(snake.head)
                self.spawnFood(self.MINIMUM_FOOD)
                snake.health = 100
                snake.length += 1
                rewards[snake.id] += 10
            else:
                snake.health -= 1
                snake.body.pop(0)
            
        '''
        We run the loop twice so that the states are post-movement
        this means one snake's decision is not valued more than the other
        50/50 odds will be selected in head-on collisions, etc.
        '''
        # Snake Head in Snake Head Death Flag
        if self.snakes[0].head == self.snakes[1].head and self.snakes[0].alive and self.snakes[1].alive:
            if self.snakes[0].length < self.snakes[1].length:
                self.snakes[0].alive = False
                rewards[0] -= 10
            elif self.snakes[0].length > self.snakes[1].length:
                self.snakes[1].alive = False
                rewards[1] -= 10
            else:
                rewards[0] -= 10
                rewards[1] -= 10
            
        # Snake Head in Enemy Snake Body Death Flag
        if (self.snakes[0].head in self.snakes[1].body[:-1] and self.snakes[1].alive):
            rewards[0] -= 10
            self.snakes[0].alive = False
        
        if (self.snakes[1].head in self.snakes[0].body[:-1] and self.snakes[0].alive):
            rewards[1] -= 10
            self.snakes[1].alive = False
            
        # Snake Head OOB Death Flag
        if (self.snakes[0].head[0] > 10 or self.snakes[0].head[0] < 0 or self.snakes[0].head[1] > 10 or self.snakes[0].head[1] < 0 and self.snakes[0].alive):
            self.snakes[0].alive = False
            rewards[0] -= 10
        if (self.snakes[1].head[0] > 10 or self.snakes[1].head[0] < 0 or self.snakes[1].head[1] > 10 or self.snakes[1].head[1] < 0 and self.snakes[1].alive):
            self.snakes[1].alive = False
            rewards[1] -= 10
            
        # Snake Health Death Flag
        if (self.snakes[0].health <= 0 and self.snakes[0].alive):
            self.snakes[0].alive = False
            rewards[0] -= 10
        
        if (self.snakes[1].health <= 0 and self.snakes[1].alive):
            self.snakes[1].alive = False
            rewards[0] -= 10

        # Add + 1 reward for each turn survived
        for i in range(len(rewards)):
            if (self.snakes[i].alive):
                rewards[i] += 1
    
        # This triggers the game to update state to the next turn
        self.updateState(rewards)
        
    def updateState(self, rewards=[0, 0]):
        self.board_matrix = np.zeros((11, 11), dtype=int)
        
        # The state matrix is the same as the board matrix
        # however each snake gets a unique state matrix describing
        # the position of the "enemy" snake uniquely
        
        # Make a state matrix for each snake
        state_matricies = []
        
        for food_location in self.food_locations:
            self.board_matrix[food_location[0]][food_location[1]] = 1
            
        for snake in self.snakes:
            if (not snake.alive):
                continue
            
            up_point = copy.copy(snake.head)
            up_point[0] -= 1
            down_point = copy.copy(snake.head)
            down_point[0] += 1
            left_point = copy.copy(snake.head)
            left_point[1] -= 1
            right_point = copy.copy(snake.head)
            right_point[1] += 1
            
            up_in_enemy = False
            down_in_enemy = False
            left_in_enemy = False
            right_in_enemy = False
            
            for enemy_snake in self.snakes:
                if (enemy_snake.id == snake.id or not enemy_snake.alive):
                    continue
                if (up_point in enemy_snake.body):
                    up_in_enemy = True
                    
                if (down_point in enemy_snake.body):
                    down_in_enemy = True
                    
                if (left_point in enemy_snake.body):
                    left_in_enemy = True
                    
                if (right_point in enemy_snake.body):
                    right_in_enemy = True
                    
            
            # Closest Food to Snake (Manhattan Distance)
            closest_food = None
            closest_distance = 1000
            for food_location in self.food_locations:
                distance = abs(food_location[0] - snake.head[0]) + abs(food_location[1] - snake.head[1])
                if (distance < closest_distance):
                    closest_distance = distance
                    closest_food = food_location
                    
            # Closest enemy snake head (Manhattan Distance)
            closest_enemy = None
            closest_distance = 1000
            for enemy_snake in self.snakes:
                if (enemy_snake.id == snake.id or not enemy_snake.alive):
                    continue
                distance = abs(enemy_snake.head[0] - snake.head[0]) + abs(enemy_snake.head[1] - snake.head[1])
                if (distance < closest_distance):
                    closest_distance = distance
                    closest_enemy = enemy_snake.head
                    
            if (closest_enemy == None):
                closest_enemy = [np.Inf, np.Inf]
            
            state = [                
                # Move Safety (Check all directions for OOB and Snake Collision)
                (up_point[0] >= 0 and up_point[0] <= 10 and up_point[1] >= 0 and up_point[1] <= 10 and up_point not in snake.body),
                (down_point[0] >= 0 and down_point[0] <= 10 and down_point[1] >= 0 and down_point[1] <= 10 and down_point not in snake.body),
                (left_point[0] >= 0 and left_point[0] <= 10 and left_point[1] >= 0 and left_point[1] <= 10 and left_point not in snake.body),
                (right_point[0] >= 0 and right_point[0] <= 10 and right_point[1] >= 0 and right_point[1] <= 10 and right_point not in snake.body),
                
                # Food Direction
                (closest_food[0] < snake.head[0]),
                (closest_food[0] > snake.head[0]),
                (closest_food[1] < snake.head[1]),
                (closest_food[1] > snake.head[1]),
                
                # Enemy Body Collision
                up_in_enemy,
                down_in_enemy,
                left_in_enemy,
                right_in_enemy,
                
                # Snake Health 
                (snake.health / 100)
            ]
            
            state_matricies.append(state)
            
            for body_part in snake.body:
                if (body_part == snake.head):
                    self.board_matrix[snake.head[0]][snake.head[1]] = 2
                else:
                    self.board_matrix[body_part[0]][body_part[1]] = 3
                    
        for (i, matrix) in enumerate(state_matricies):
            self.snakes[i].setState(matrix, rewards[i])
            
    def spawnSnakes(self):
        # This handles spawning in snakes at the beginning of a game
        snake_head_locations = np.random.randint(0, 11, (2, 2))
        while snake_head_locations[0] is snake_head_locations[1]:
            snake_head_locations = np.random.randint(0, 11, (2, 2))
        
        snake_idx = 0
        for snake_head in snake_head_locations:
            # If snakes already exist, reset them instead of creating new ones
            if len(self.snakes) == self.NUMBER_SNAKES:
                self.snakes[snake_idx].resetSnake([snake_head[0], snake_head[1]])
                self.board_matrix[snake_head[0]][snake_head[1]] = 2
            else:
                self.snakes.append(Snake([snake_head[0], snake_head[1]], snake_idx))
                self.board_matrix[snake_head[0]][snake_head[1]] = 2
                
            snake_idx += 1
    
    def spawnFood(self, numFood):
        # This spawns food until the number of food in self.food_locations
        # matches numFood
        while(len(self.food_locations) < numFood):
            random_location = np.random.randint(0, 11, (1, 2))[0]
            if (self.board_matrix[random_location[0]][random_location[1]] == 0):
                self.food_locations.append([random_location[0], random_location[1]])
                self.board_matrix[random_location[0]][random_location[1]] = 1
    
    def drawState(self):
        clear() # Clears console
        for x in range(self.board_matrix.shape[0]):
            for y in range(self.board_matrix.shape[1]):
                if (self.board_matrix[x][y] == 0):
                    print("▢ ", end="")
                elif (self.board_matrix[x][y] == 1):
                    print("🍒", end="")
                elif (self.board_matrix[x][y] == 2):
                    print("👶", end="")
                elif (self.board_matrix[x][y] == 3):
                    print("⛔", end="")
            print("")
        print("Game: {}".format(self.game_number))
        print("Turn: {}".format(self.turn))
        for snake in self.snakes:
            print("Snake {}: Health: {} Length: {} Alive: {}".format(snake.id, snake.health, snake.length, snake.alive))
        time.sleep(self.SIMULATION_SPEED)
    
    def play(self, drawState):
        # This calls nextTurn in a loop until all snakes are dead
        self.resetGame()
        
        # Check if any self.snakes are alive
        while (any([snake.alive for snake in self.snakes])):
            if (drawState):
                self.drawState()
            self.nextTurn()
            
        # We should return scores here
        return copy.copy(self.snakes)