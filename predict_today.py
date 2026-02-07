import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import leaguedashteamstats
import re, torch, time
from brain import NBABrain

def run_analysis():
    print(">>> Инициализация парсинга NBA Stats...")
    
    # Парсим расширенную статистику
    try:
        raw_stats = leaguedashteamstats.LeagueDashTeamStats(season='2025-26', timeout=60).get_data_frames()[0]
        # Собираем всё: PTS, REB, AST, BLK, STL, TOV
        stats_map = raw_stats.set_index('TEAM_ID').to_dict('index')
    except Exception as e:
        print(f">>> ERROR_PARSING: {e}")
        return

    # Загрузка модели
    try:
        model = NBABrain(100)
        model.load_state_dict(torch.load('nba_model_2026.pth', map_location='cpu'))
        model.eval()
    except: model = None

    # Парсим текущее табло
    games = scoreboard.ScoreBoard().games.get_dict()
    cards_html = ""

    for g in games:
        h_id, a_id = g['homeTeam']['teamId'], g['awayTeam']['teamId']
        h_s = stats_map.get(h_id, {})
        a_s = stats_map.get(a_id, {})

        # ИИ Прогноз (упрощенная логика на основе PTS/AST/BLK для примера)
        prob = 0.5
        if h_s and a_s:
            # Считаем разницу по ключевым параметрам
            diff = (h_s['PTS'] - a_s['PTS']) + (h_s['BLK'] - a_s['BLK']) + (h_s['AST'] - a_s['AST'])
            prob = 1 / (1 + torch.exp(torch.tensor(-diff/10))).item()

        win_pct = int(prob * 100)

        cards_html += f"""
        <div class="card">
            <div class="teams">{g['awayTeam']['teamName']} @ {g['homeTeam']['teamName']}</div>
            <div class="stats-grid">
                <span class="label">ОЧКИ (AVG):</span><span class="val">{a_s.get('PTS')} | {h_s.get('PTS')}</span>
                <span class="label">ПЕРЕДАЧИ:</span><span class="val">{a_s.get('AST')} | {h_s.get('AST')}</span>
                <span class="label">ПОДБОРЫ:</span><span class="val">{a_s.get('REB')} | {h_s.get('REB')}</span>
                <span class="label">БЛОКИ:</span><span class="val">{a_s.get('BLK')} | {h_s.get('BLK')}</span>
            </div>
            <div class="prediction-box">
                AI_PROBABILITY: {win_pct}% (HOME_ADVANTAGE)
                <div class="bar-container"><div class="bar-fill" style="width: {win_pct}%"></div></div>
            </div>
        </div>
        """

    # Запись в HTML
    with open('index.html', 'r', encoding='utf-8') as f: content = f.read()
    updated = re.sub(r".*?", f"\n{cards_html}\n", content, flags=re.DOTALL)
    with open('index.html', 'w', encoding='utf-8') as f: f.write(updated)
    print(">>> DATA_SYNC_COMPLETE")

if __name__ == "__main__":
    run_analysis()
