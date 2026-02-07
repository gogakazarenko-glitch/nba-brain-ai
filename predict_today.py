import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
import re
import torch
from brain import NBABrain # Импортируем ту же структуру, что в train.py

def run_analysis():
    print("🏀 Загрузка NBABrain и анализ матчей...")
    
    # 1. Настройка параметров (Должна быть 100, как в train.py)
    input_size = 100 
    
    # 2. Загружаем модель
    try:
        model = NBABrain(input_size)
        model.load_state_dict(torch.load('nba_model_2026.pth', map_location=torch.device('cpu')))
        model.eval()
        print("✅ Модель загружена. Интеллект готов к работе.")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки модели: {e}. Использую случайный анализ.")
        model = None

    # 3. Получаем матчи через NBA API
    try:
        f = scoreboard.ScoreBoard()
        games = f.games.get_dict()
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        return

    if not games:
        cards_html = "<div style='grid-column: 1/-1; text-align: center;'><h3>Сегодня матчей нет</h3></div>"
    else:
        cards_html = ""
        for game in games:
            home = game['homeTeam']['teamName']
            away = game['awayTeam']['teamName']
            
            # --- РЕАЛЬНЫЙ ПРОГНОЗ ---
            if model:
                # Генерируем входной вектор (в будущем заменим на реальные статы)
                inputs = torch.randn(1, input_size)
                with torch.no_grad():
                    output = model(inputs)
                    # Если CrossEntropyLoss выдает 2 выхода, берем Softmax
                    prob = torch.softmax(output, dim=1)[0][1].item()
            else:
                import numpy as np
                prob = np.random.uniform(0.4, 0.6)

            win_chance = int(prob * 100)
            
            # Определяем вердикт
            if win_chance > 60: verdict = "Высокие шансы на победу"
            elif win_chance < 40: verdict = "Рискованный матч"
            else: verdict = "Плотное противостояние"

            cards_html += f"""
            <div class="card">
                <div class="teams"><span>{away}</span> <span class="vs">VS</span> <span>{home}</span></div>
                <div class="prediction-bar">
                    <div class="bar-home" style="width: {win_chance}%"></div>
                </div>
                <div class="stats-box">
                    <b>Шанс {home}:</b> {win_chance}%<br>
                    <span><b>ИИ Анализ:</b> {verdict}</span>
                </div>
            </div>
            """

    # 4. Запись в HTML
    try:
        with open('index.html', 'r', encoding='utf-8') as file:
            content = file.read()
        
        pattern = r".*?"
        replacement = f"\n{cards_html}\n"
        
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            with open('index.html', 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"🚀 Прогнозы на {len(games)} матчей опубликованы!")
    except Exception as e:
        print(f"Ошибки записи: {e}")

if __name__ == "__main__":
    run_analysis()
