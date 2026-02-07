import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
import os

def run_analysis():
    print("Проверка расписания матчей...")
    try:
        f = scoreboard.ScoreBoard()
        games = f.games.get_dict()
    except Exception as e:
        print(f"Ошибка API: {e}")
        return

    if not games:
        print("API не вернуло матчей на текущий момент.")
        cards_html = "<p style='text-align:center;'>Матчи не найдены или лига в режиме ожидания.</p>"
    else:
        print(f"Найдено матчей: {len(games)}")
        cards_html = ""
        for game in games:
            home = game['homeTeam']['teamName']
            away = game['awayTeam']['teamName']
            # Здесь имитируем прогноз нейронки (для теста)
            cards_html += f"""
            <div class="card">
                <div class="teams"><span>{away}</span> <span class="vs">VS</span> <span>{home}</span></div>
                <div class="prediction-bar"><div class="bar-home" style="width: 55%"></div></div>
                <div class="stats-box"><b>Прогноз ИИ:</b> Анализ завершен успешно.</div>
            </div>
            """

    # Читаем HTML
    with open('index.html', 'r', encoding='utf-8') as file:
        content = file.read()

    # МЕТКА ДЛЯ ЗАМЕНЫ
    marker = ''
    
    if marker in content:
        new_content = content.replace(marker, cards_html + "\n" + marker)
        with open('index.html', 'w', encoding='utf-8') as file:
            file.write(new_content)
        print("Данные успешно записаны в index.html!")
    else:
        print("ОШИБКА: Метка не найдена в index.html. Верни её в файл!")

if __name__ == "__main__":
    run_analysis()
