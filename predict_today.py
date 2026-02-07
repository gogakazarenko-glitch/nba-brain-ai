import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
import re

def run_analysis():
    print("Запуск анализа матчей...")
    try:
        f = scoreboard.ScoreBoard()
        games = f.games.get_dict()
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return

    if not games:
        print("Матчей на сегодня не найдено.")
        cards_html = "<div style='grid-column: 1/-1; text-align: center;'><h3>Сегодня матчей нет</h3></div>"
    else:
        print(f"Найдено матчей: {len(games)}")
        cards_html = ""
        for game in games:
            home = game['homeTeam']['teamName']
            away = game['awayTeam']['teamName']
            # Здесь твоя нейронка делает прогноз (заглушка для примера)
            cards_html += f"""
            <div class="card">
                <div class="teams"><span>{away}</span> <span class="vs">VS</span> <span>{home}</span></div>
                <div class="prediction-bar"><div class="bar-home" style="width: 50%"></div></div>
                <div class="stats-box"><b>ИИ Прогноз:</b> Ожидается плотная игра.</div>
            </div>
            """

    # Читаем текущий HTML
    try:
        with open('index.html', 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print("Ошибка: index.html не найден!")
        return

    # Регулярное выражение для поиска текста между START и END
    pattern = r".*?"
    replacement = f"\n{cards_html}\n"
    
    # Делаем замену
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open('index.html', 'w', encoding='utf-8') as file:
            file.write(new_content)
        print("Сайт успешно обновлен!")
    else:
        print("ОШИБКА: Метки и не найдены в index.html!")

if __name__ == "__main__":
    run_analysis()
