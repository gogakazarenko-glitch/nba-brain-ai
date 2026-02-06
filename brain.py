import torch
import torch.nn as nn
import torch.nn.functional as F

class NBABrain(nn.Module):
    def __init__(self, input_size):
        super(NBABrain, self).__init__()
        
        # 1. Первый слой: принимает все данные (статы + физика + психология)
        self.fc1 = nn.Linear(input_size, 128)
        
        # 2. Второй слой: ищет скрытые связи между ростом и усталостью
        self.fc2 = nn.Linear(128, 64)
        
        # 3. Третий слой: анализирует влияние тренера и мотивации
        self.fc3 = nn.Linear(64, 32)
        
        # 4. Выходной слой: выдает два числа (Шанс победы Команды А и Команды Б)
        self.output = nn.Linear(32, 2)
        
        # Dropout помогает нейронке не "зубрить" данные, а реально думать
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        # Прогоняем данные через слои с функцией активации ReLU
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        
        x = F.relu(self.fc3(x))
        
        # На выходе используем Softmax, чтобы получить вероятность в %
        return F.softmax(self.output(x), dim=1)

# Пример инициализации:
# Если у нас 50 параметров на входе (статы 10 игроков + тренеры + усталость)
# model = NBABrain(input_size=50)