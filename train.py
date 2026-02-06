import torch
import torch.nn as nn
import torch.optim as optim
from brain import NBABrain # Импортируем нашу архитектуру
import numpy as np

# 1. Подготовка данных (имитация собранного датасета за 2024-26)
# В реальности сюда загружается твой CSV файл
def train_model():
    # Допустим, у нас 100 параметров на входе (статы, физика, новости)
    input_size = 100 
    model = NBABrain(input_size)
    
    # Оптимизатор Adam — он самый эффективный для таких задач
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    # Функция потерь (ошибки)
    criterion = nn.CrossEntropyLoss()

    print("Начинаю обучение нейронки на данных 2024-2026...")

    # Цикл обучения (Эпохи)
    for epoch in range(100): # Нейронка просмотрит все матчи 100 раз
        # Здесь мы имитируем входные данные (X) и реальный результат (y)
        # В рабочем коде здесь будет загрузка из data_integrator.py
        inputs = torch.randn(32, input_size) # Батч из 32 матчей
        labels = torch.randint(0, 2, (32,)) # Реальные победители (0 или 1)

        # Обнуляем градиенты
        optimizer.zero_grad()
        
        # Прямой проход: нейронка делает прогноз
        outputs = model(inputs)
        
        # Считаем ошибку
        loss = criterion(outputs, labels)
        
        # Обратный проход: исправляем ошибки
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f'Эпоха [{epoch+1}/100], Ошибка: {loss.item():.4f}')

    # Сохраняем "обученный мозг" в файл
    torch.save(model.state_dict(), 'nba_model_2026.pth')
    print("Обучение завершено! Модель сохранена в файл nba_model_2026.pth")

if __name__ == "__main__":
    train_model()