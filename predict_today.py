import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import leaguedashteamstats
import re
import torch
import time
from brain import NBABrain

# 1. Функция сбора детальной статистики (твой код здесь)
def get_detailed_nba_stats():
    headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.nba.com/',
    }
    print("📊 Загрузка детальной статистики (PTS, REB, BLK)...")
    try:
        # Запрашиваем данные за сезон 2025-26
        stats = leaguedashteamstats.LeagueDashTeamStats(
            season='2025-26', 
            measure_type_detailed_defense='Base'
        ).get_data_frames()[0]
        
        needed_columns = ['TEAM_ID', 'TEAM_NAME', 'PTS', 'REB', 'AST', 'BLK', 'MIN']
        return stats[needed_columns]
    except Exception as e:
        print(f"❌ Ошибка загрузки статов: {e}")
        return None

def run_analysis():
    # Получаем таблицу со статистикой один раз за запуск
    stats_df = get_detailed_nba_stats()
    
    # Подключаем "мозг"
    input_size = 100
    try:
        model = NBABrain(input_size)
        model.load_state_dict(torch.load('nba_model_2026.pth', map_location=torch.device('cpu')))
        model.eval()
    except:
        model = None

    # Получаем сегодняшние матчи
    try:
        f = scoreboard.ScoreBoard()
        games = f.games.get_dict()
    except: return

    cards_html = ""
    for game in games:
        h_id = game['homeTeam']['teamId']
        a_id = game['awayTeam']['teamId']
        h_name = game['homeTeam']['teamName']
        a_name = game['awayTeam']['teamName']

        # Извлекаем конкретные цифры для команд из нашей таблицы
        h_data = stats_df[stats_df['TEAM_ID'] == h_id].iloc[0] if stats_df is not None else None
        a_data = stats_df[stats_df['TEAM_ID'] == a_id].iloc[0] if stats_df is not None else None

        # Формируем прогноз (если данные есть)
        if h_data is not None and a_data is not None:
            # Здесь мы подаем реальные цифры в модель
            # Напр: [Очки_дом, Подборы_дом, Блоки_дом, Очки_гости, ...]
            # Для примера возьмем отношение их очков
            prob = (h_data['PTS'] / (h_data['PTS'] + a_data['PTS']))
        else:
            prob = 0.5
        
        win_chance = int(prob * 100)

        # Рисуем карточку с реальными статами
        cards_html += f"""
        <div class="card">
            <div class="teams"><span>{a_name}</span> <span class="vs">VS</span> <span>{h_name}</span></div>
            <div class="prediction-bar"><div class="bar-home" style="width: {win_chance}%"></div></div>
            <div class="stats-box">
                <div style="display:flex; justify-content:space-between; font-size: 0.8em;">
                    <span>PTS: {a_data['PTS'] if a_data is not None else '??'}</span>
                    <span>BLK: {a_data['BLK'] if a_data is not None else '??'}</span>
                    <span style="color:#f57c00;">|</span>
                    <span>PTS: {h_data['PTS'] if h_data is not None else '??'}</span>
                    <span>BLK: {h_data['BLK'] if h_data is not None else '??'}</span>
                </div>
                <hr style="border:0; border-top:1px solid #444; margin: 10px 0;">
                <b>Прогноз {h_name}:</b> {win_chance}%
            </div>
        </div>
        """

    # Запись в index.html (твой стандартный блок)
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = re.sub(r".*?", f"\n{cards_html}\n", content, flags=re.DOTALL)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("🚀 Глубокий анализ завершен и опубликован!")

if __name__ == "__main__":
    run_analysis()
