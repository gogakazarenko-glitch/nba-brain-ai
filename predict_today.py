import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import leaguedashteamstats
import re, torch, time

def run_analysis():
    print(">>> Запуск процесса глубокой аналитики...")
    
    # 1. Сбор расширенной статистики (PTS, REB, AST, BLK)
    try:
        raw = leaguedashteamstats.LeagueDashTeamStats(season='2025-26', timeout=60).get_data_frames()[0]
        stats_map = raw.set_index('TEAM_ID').to_dict('index')
    except Exception as e:
        print(f">>> API ERROR: {e}"); return

    # 2. Получение текущих матчей
    try:
        games = scoreboard.ScoreBoard().games.get_dict()
    except: return

    cards_html = ""
    for g in games:
        h_id, a_id = g['homeTeam']['teamId'], g['awayTeam']['teamId']
        h_name, a_name = g['homeTeam']['teamName'], g['awayTeam']['teamName']
        h_s, a_s = stats_map.get(h_id), stats_map.get(a_id)

        if h_s and a_s:
            # Расчет вероятности на основе средних показателей (PPG)
            h_ppg, a_ppg = h_s['PTS']/h_s['GP'], a_s['PTS']/a_s['GP']
            h_bpg, a_bpg = h_s['BLK']/h_s['GP'], a_s['BLK']/a_s['GP']
            
            # Математический вес (Сигмоида)
            diff = (h_ppg - a_ppg) * 0.3 + (h_bpg - a_bpg) * 0.7 + 2.0 
            win_pct = int(torch.sigmoid(torch.tensor(diff)).item() * 100)
            win_pct = min(max(win_pct, 12), 88) # Реалистичные границы

            # Текстовый анализ от ИИ
            verdict = f"ИИ анализ: {'превосходство в защите' if h_bpg > a_bpg else 'высокий темп атаки'} у {h_name if h_ppg > a_ppg else a_name}."
        else:
            win_pct, verdict = 50, "Данные калибруются..."

        cards_html += f"""
        <div class="card">
            <div class="teams">{a_name} @ {h_name}</div>
            <div class="stats-grid">
                <span class="label">AVG PTS:</span><span class="val">{a_ppg:.1f} | {h_ppg:.1f}</span>
                <span class="label">BLOCKS:</span><span class="val">{a_bpg:.1f} | {h_bpg:.1f}</span>
                <span class="label">REB/G:</span><span class="val">{(a_s['REB']/a_s['GP']):.1f} | {(h_s['REB']/h_s['GP']):.1f}</span>
            </div>
            <div class="prediction-box">
                <div style="font-weight:bold; margin-bottom:8px;">ВЕРОЯТНОСТЬ: {win_pct}%</div>
                <div class="bar-container"><div class="bar-fill" style="width: {win_pct}%"></div></div>
                <div style="margin-top:10px; font-size:0.8em; color:#00ff41; border-left: 1px solid #333; padding-left:8px;">{verdict}</div>
            </div>
        </div>
        """

    # 3. Жесткая перезапись файла (АНТИ-ДУБЛЬ)
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Разрезаем файл по маркерам
        head = content.split('')[0]
        tail = content.split('')[-1]
        
        # Склеиваем заново: Голова + Новые карточки + Хвост
        new_html = head + "\n" + cards_html + "\n" + tail
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(">>> SYNC_SUCCESS: Сайт обновлен.")
    except Exception as e:
        print(f">>> WRITE_ERROR: {e}")

if __name__ == "__main__":
    run_analysis()
