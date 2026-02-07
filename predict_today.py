import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import leaguedashteamstats
import re, torch, time

def get_expert_analysis(h_s, a_s, h_name, a_name):
    """Генерация текстового разбора"""
    h_ppg = h_s['PTS'] / h_s['GP']
    a_ppg = a_s['PTS'] / a_s['GP']
    
    analysis = []
    if h_ppg > a_ppg:
        analysis.append(f"Атакующий потенциал {h_name} выше ({h_ppg:.1f} PPG)")
    else:
        analysis.append(f"{a_name} превосходит в наборе очков ({a_ppg:.1f} PPG)")
        
    if h_s['BLK'] / h_s['GP'] > a_s['BLK'] / a_s['GP']:
        analysis.append("сильная защита под кольцом")
    
    return "Экспертный разбор: " + ", ".join(analysis) + ". Модель прогнозирует доминирование по ключевым метрикам."

def run_analysis():
    print(">>> SYSTEM START: Глубокий парсинг данных...")
    
    try:
        # Получаем данные за сезон
        raw = leaguedashteamstats.LeagueDashTeamStats(season='2025-26', timeout=60).get_data_frames()[0]
        stats_map = raw.set_index('TEAM_ID').to_dict('index')
    except Exception as e:
        print(f">>> API ERROR: {e}"); return

    try:
        games_dict = scoreboard.ScoreBoard().games.get_dict()
    except: return

    cards_html = ""
    for g in games_dict:
        h_id, a_id = g['homeTeam']['teamId'], g['awayTeam']['teamId']
        h_name, a_name = g['homeTeam']['teamName'], g['awayTeam']['teamName']
        h_s, a_s = stats_map.get(h_id), stats_map.get(a_id)

        if h_s and a_s:
            # Расчет вероятности (нормализованный)
            h_score = (h_s['PTS']/h_s['GP']) * 0.4 + (h_s['REB']/h_s['GP']) * 0.3 + (h_s['BLK']/h_s['GP']) * 0.3
            a_score = (a_s['PTS']/a_s['GP']) * 0.4 + (a_s['REB']/a_s['GP']) * 0.3 + (a_s['BLK']/a_s['GP']) * 0.3
            
            diff = (h_score - a_score) + 2.0 # +2 за домашнюю площадку
            win_pct = int(torch.sigmoid(torch.tensor(diff)).item() * 100)
            win_pct = min(max(win_pct, 10), 90) # Ограничитель 10-90%
            
            ai_verdict = get_expert_analysis(h_s, a_s, h_name, a_name)
            
            cards_html += f"""
            <div class="card">
                <div class="teams">{a_name} @ {h_name}</div>
                <div class="stats-grid">
                    <span class="label">AVG PTS:</span><span class="val">{a_s['PTS']/a_s['GP']:.1f} | {h_s['PTS']/h_s['GP']:.1f}</span>
                    <span class="label">REB/G:</span><span class="val">{a_s['REB']/a_s['GP']:.1f} | {h_s['REB']/h_s['GP']:.1f}</span>
                    <span class="label">BLK/G:</span><span class="val">{a_s['BLK']/a_s['GP']:.1f} | {h_s['BLK']/h_s['GP']:.1f}</span>
                </div>
                <div class="prediction-box">
                    <div style="font-weight:bold; color:#00ff41; margin-bottom:10px;">PROBABILITY: {win_pct}%</div>
                    <div class="bar-container"><div class="bar-fill" style="width: {win_pct}%"></div></div>
                    <div style="margin-top:15px; font-size:0.85em; border-left: 1px solid #00ff41; padding-left:10px;">{ai_verdict}</div>
                </div>
            </div>
            """

    # --- ЖЕСТКАЯ ОЧИСТКА И ЗАПИСЬ ---
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Разрезаем файл по меткам и выбрасываем СТАРОЕ содержимое
        start_marker = ""
        end_marker = ""
        
        if start_marker in content and end_marker in content:
            head = content.split(start_marker)[0]
            tail = content.split(end_marker)[-1]
            new_html = head + start_marker + "\n" + cards_html + "\n" + end_marker + tail
            
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(new_html)
            print(">>> SYNC SUCCESS: Данные обновлены без дублей.")
    except Exception as e:
        print(f">>> WRITE ERROR: {e}")

if __name__ == "__main__":
    run_analysis()
