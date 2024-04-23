from dqn import DQN
import torch
import random
import copy

class Snake():
    def __init__(self, head_position, id) -> None:
        # Snake Info
        self.id = id
        self.alive = True
        self.health = 100
        self.length = 3
        self.turns = 0
        self.head = head_position
        self.body = [copy.copy(head_position)]
        self.last_action = None
        self.state = None
        self.food_reward = 0
        self.accumulated_reward = 0
        
        # DQN Agent Information
        self.n_actions = 4 # Up, Down, Left, Right
        self.n_observations = 18
        self.epsilon = 1 # Randomness
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.999
        self.gamma = 0.9 # Discount Rate
        self.lr = 0.001 # Learning Rate
        self.batch_size = 1000
        self.model = DQN(self.n_observations, self.n_actions)
        self.trainer = DQN.Trainer(self.model, self.lr, self.gamma)
        self.memory = DQN.ReplayMemory(100_000)
    
    # WARNING: This function trains the model
    def resetSnake(self, new_head_position):
        self.alive = True
        self.health = 100
        self.length = 3
        self.accumulated_reward = 0
        self.food_reward = 0
        self.head = new_head_position
        self.body = [copy.copy(self.head)]
        self._train_long_memory()
    
    
    def setState(self, new_state, reward) -> None:
        old_state = copy.deepcopy(self.state)
        self.state = new_state
        
        self.accumulated_reward += reward
        
        if (old_state is None):
            return
            
        
        self._train_short_memory(old_state, self.last_action, reward, self.state)
        self._remember(old_state, self.last_action, self.state, reward)
        
    def _remember(self, state, action, next_state, reward) -> None:
        self.memory.append(state, action, reward, next_state, copy.copy(self.alive))
    
    def _train_long_memory(self) -> None:
        if len(self.memory) > self.batch_size:
            mini_sample = self.memory.sample(self.batch_size)
        else:
            mini_sample = self.memory.sample(len(self.memory))
        
        if len(mini_sample) == 0:
            return
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        
    def _train_short_memory(self, state, action, reward, next_state) -> None:
        self.trainer.train_step(state, action, reward, next_state, self.alive)
        
    def _get_action(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        move_encoding = [0, 0, 0, 0] # Up, Down, Left, Right
        if (random.uniform(0, 1) < self.epsilon):
            move = random.randint(0, 3)
            move_encoding[move] = 1
        else:
            state0 = torch.tensor(self.state, dtype=torch.float).to(self.model.device)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            move_encoding[move] = 1
        return move_encoding
           
    def getMove(self) -> str:
        self.turns += 1
        
        if (len(self.body) != self.length):
            self.body.append(copy.copy(self.body[-1]))
            
        # Get User Input
        # movement_to_make = input("Enter a move: ")
        # if (movement_to_make == "w"):
        #     self.last_action = [1, 0, 0, 0]
        #     return "UP"
        # elif (movement_to_make == "s"):
        #     self.last_action = [0, 1, 0, 0]
        #     return "DOWN"
        # elif (movement_to_make == "a"):
        #     self.last_action = [0, 0, 1, 0]
        #     return "LEFT"
        # elif (movement_to_make == "d"):
        #     self.last_action = [0, 0, 0, 1]
        #     return "RIGHT"
        
        
        
        self.last_action = self._get_action()
        if self.last_action == [1, 0, 0, 0]:
            return "UP"
        elif self.last_action == [0, 1, 0, 0]:
            return "DOWN"
        elif self.last_action == [0, 0, 1, 0]:
            return "LEFT"
        elif self.last_action == [0, 0, 0, 1]:
            return "RIGHT"
        else:
            return "UP"
