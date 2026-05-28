import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

'''
model 은 hidden layer가 하나 있는 MLP
RELU 말고 Tanh 할수 있으면 ㄱㄱ (느려지긴 할듯) 
- relu면 음수 input 학습이 안됨

Relu로 한다. input을 바꿔서 0 또는 1로만 넣게 함 (심플) 
CNN 구조를 이용해야 locality를 활용할 수 있을수도


모델 평가나 예측(inference) 용도로 사용할 때는 반드시 model.eval() 를 사용해서 'evaluation model'로 설정해주어야 합니다. 
그렇지 않으면 예측을 할 때마다 dropout 과 batch normalization이 바뀌어서 예측값이 바뀌게 됩니다.
만약 모델 훈련을 계속 이어서 하고자 한다면, model.train() 을 사용해서 'training model'로 설정해서 데이터로 부터 계속 Epoch을 반복하면서 학습을 통해 파라미터의 가중치를 업데이트 해주면 됩니다.

https://wikidocs.net/295754

https://rfriend.tistory.com/820
'''

class Linear_QNet(nn.Module):
    modelID = 0
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)
        self.modelID = Linear_QNet.modelID
        Linear_QNet.modelID += 1

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        file_name = 'model{}.pth'.format(self.modelID)
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        # 1: predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new

        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()


