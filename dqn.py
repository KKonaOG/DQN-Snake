'''
A large majority of this file was adapted from the example at:
https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

As well as the following medium article:
https://medium.com/@nancy.q.zhou/teaching-an-ai-to-play-the-snake-game-using-reinforcement-learning-6d2a6e8f3b1c
'''

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import random
from collections import deque

class DQN(nn.Module):
    class ReplayMemory(object):
        def __init__(self, capacity) -> None:
            self.memory = deque(maxlen=capacity)
        
        def append(self, state, action, reward, next_state, alive):
            """ Save a transition """
            self.memory.append((state, action, reward, next_state, alive))
        
        def sample(self, batch_size):
            return random.sample(self.memory, batch_size)
        
        def __len__(self):
            return len(self.memory)
        
    class Trainer():
        def __init__(self, model, lr, gamma) -> None:
            self.model = model
            self.lr = lr
            self.gamma = gamma
            self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
            self.criterion = nn.MSELoss() # Loss Function
        
        def train_step(self, state, action, reward, next_state, done):
            # Convert to PyTorch Tensors
            state = torch.tensor(state, dtype=torch.float).to(self.model.device)
            next_state = torch.tensor(next_state, dtype=torch.float).to(self.model.device)
            action = torch.tensor(action, dtype=torch.long).to(self.model.device)
            reward = torch.tensor(reward, dtype=torch.float).to(self.model.device)
            
            if len(state.shape) == 1:
                state = state.unsqueeze(0)
                next_state = next_state.unsqueeze(0)
                action = action.unsqueeze(0)
                reward = reward.unsqueeze(0)
                done = (done,)
            
            prediction = self.model(state)
            
            target = prediction.clone()
            for idx in range(len(done)):
                Q_new = reward[idx]
                if not done[idx]:
                    Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
                target[idx][torch.argmax(action[idx]).item()] = Q_new
            
            self.optimizer.zero_grad()
            loss = self.criterion(prediction, target)
            loss.backward()
            self.optimizer.step()
    
    def __init__(self, n_observations, n_actions) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, 256).to(self.device)
        self.layer2 = nn.Linear(256, 256).to(self.device)
        self.layer3 = nn.Linear(256, n_actions).to(self.device)
    
    def forward(self, x):
        x = F.relu(self.layer1(x)).to(self.device)
        x = F.relu(self.layer2(x)).to(self.device)
        x = self.layer3(x).to(self.device)
        return x
    
    def save(self, file_name):
        torch.save(self.state_dict(), file_name)