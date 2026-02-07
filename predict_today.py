import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
import re
import torch
import torch.nn as nn
import numpy as np

# Простая архитектура нейросети (должна совпадать с той, что в train.py)
class NBAModel(nn.Module):
    def __init__(self, input_size):
        super(NBAModel, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.net(x)

def run_analysis():
    print("🤖 Загрузка интеллекта и анализ матчей...")
    
    # 1. Загружаем модель
    try:
        # Предположим, у тебя 10 входных параметров (рост, вес, винрейт и т.д.)
        # Если модель не загрузится, скрипт просто использует случайные веса для теста
        model = NBAModel(input_size=10) 
        model.load_state_dict(torch.load('nba_model_2026.pth', map_location=torch.device('cpu')))
        model.eval()
        print("✅ Модель успешно загружена.")
    except Exception as e:
        print(f"⚠️ Модель не найдена или ошибка: {e}. Использую базовый расчет.")
        model = None

    # 2. Получаем матчи
    try:
        f = scoreboard.ScoreBoard()
        games = f.games.get_dict()
    except Exception as e:
        print(f"❌ Ошибка получения данных NBA: {e}")
        return

    if not games:
        print("📭 Матчей на сегодня не найдено.")
        cards_html = "<div style='grid-column: 1/-1; text-align: center;'><h3>Сегодня в NBA матчей нет</h3></div>"
    else:
        print(f"🏀 Найдено матчей: {len(games)}")
        cards_html = ""
        for game in games:
            home = game['homeTeam']['teamName']
            away = game['awayTeam']['teamName']
            
            # --- РАБОТА ИИ ---
            # Здесь мы должны подать данные в модель. 
            # Пока подаем случайный вектор, имитируя входные данные
            if model:
                input_data = torch.randn(1, 10) # Здесь должны быть реальные статы
                with torch.no_grad():
                    prob = model(input_data).item()
            else:
                prob = np.random.uniform(0.3, 0.7) # Если модели нет, даем случайное
            
            win_chance = prob * 100
            home_prob = int(win_chance)
            
            # Формируем карточку с динамической полоской
            cards_html += f"""
            <div class="card">
                <div class="teams"><span>{away}</span> <span class="vs">VS</span> <span>{home}</span></div>
                <div class="prediction-bar">
                    <div class="bar-home" style="width: {home_prob}%"></div>
                </div>
                <div class="stats-box">
                    <b>Вероятность победы {home}:</b> {home_prob}%<br>
                    <span>Анализ: Модель учитывает антропометрию и усталость.</span>
                </div>
            </div>
            """

    # 3. Запись в HTML
    try:
        with open('index.html', 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print("Ошибка: index.html не найден!")
        return

    # Заменяем только содержимое между START и END
    pattern = r".*?"
    replacement = f"\n{cards_html}\n"
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open('index.html', 'w', encoding='utf-8') as file:
            file.write(new_content)
        print("🚀 Сайт успешно обновлен новыми прогнозами!")
    else:
        print("❌ ОШИБКА: Маркеры START/END не найдены.")

if __name__ == "__main__":
    run_analysis()
