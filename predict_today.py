import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import leaguedashteamstats
import re, torch, time, os
from brain import NBABrain

def get_ai_verdict(h_s, a_s, h_name, a_name):
    """Генерация текстового разбора на основе цифр"""
    reasons = []
    # Анализ атаки
    if h_s['PTS'] > a_s['PTS']: reasons.append(f"{h_name} эффективнее в атаке")
    else: reasons.append(f"{a_name} набирает больше в среднем")
    
    # Анализ защиты (блоки)
    if h_s['BLK'] > a_s['BLK']: reasons.append(f"доминирование {h_name} под кольцом")
    
    # Анализ командной игры
    if h_s['AST'] > a_s['AST']: reasons.append(f"лучшее движение мяча у хозяев")
    
    analysis = "Анализ завершен: " + ", ".join(reasons[:2]) + ". Ожидается тактическая борьба."
    return analysis

def run_analysis():
    print(">>> Запуск глубокого AI-анализа...")
    
    try:
        raw_stats = leaguedashteamstats.LeagueDashTeamStats(season='2025-26', timeout=60).get_data_frames()[0]
        stats_map = raw_stats.set_index('TEAM_ID').to_dict('index')
    except Exception as e:
        print(f">>> Ошибка сбора данных: {e}")
        return

    try:
        games = scoreboard.ScoreBoard().games.get_dict()
    except: return

    cards_html = ""
    for g in games:
        h_id, a_id = g['homeTeam']['teamId'], g['awayTeam']['teamId']
        h_name, a_name = g['homeTeam']['teamName'], g['awayTeam']['teamName']
        h_s = stats_map.get(h_id, {})
        a_s = stats_map.get(a_id, {})

        if h_s and a_s:
            # Улучшенная формула вероятности (Sigmoid)
            diff = (h_s['PTS'] - a_s['PTS']) * 0.1 + (h_s['BLK'] - a_s['BLK']) * 0.5
            prob = torch.sigmoid(torch.tensor(diff)).item()
            # Ограничиваем края, чтобы не было 0 или 100
            win_pct = int(min(max(prob * 100, 5), 95))
            
            # Генерируем "человеческий" вердикт
            ai_text = get_ai_verdict(h_s, a_s, h_name, a_name)
        else:
            win_pct, ai_text = 50, "Недостаточно данных для глубокого анализа."

        cards_html += f"""
        <div class="card">
            <div class="teams">{a_name} @ {h_name}</div>
            <div class="stats-grid">
                <span class="label">ОЧКИ:</span><span class="val">{a_s.get('PTS', 0)} | {h_s.get('PTS', 0)}</span>
                <span class="label">БЛОКИ:</span><span class="val">{a_s.get('BLK', 0)} | {h_s.get('BLK', 0)}</span>
                <span class="label">ПЕРЕДАЧИ:</span><span class="val">{a_s.get('AST', 0)} | {h_s.get('AST', 0)}</span>
            </div>
            <div class="prediction-box">
                <div style="margin-bottom: 10px;"><strong>ВЕРОЯТНОСТЬ: {win_pct}%</strong></div>
                <div class="bar-container"><div class="bar-fill" style="width: {win_pct}%"></div></div>
                <div style="margin-top: 10px; font-style: italic; color: #aaa;">{ai_text}</div>
            </div>
        </div>
        """

    # --- ЖЕСТКАЯ ЗАПИСЬ БЕЗ ПОВТОРОВ ---
    with open('index.html', 'r', encoding='utf-8') as f:
        full_content = f.read()

    # Если файл уже раздут (больше 50кб), вырезаем всё лишнее
    if len(full_content) > 50000:
        print(">>> Очистка переполненного файла...")
        head = full_content.split('')[0]
        tail = full_content.split('')[-1]
        new_content = head + "\n" + cards_html + "\n" + tail
    else:
        new_content = re.sub(r".*?", f"\n{cards_html}\n", full_content, flags=re.DOTALL)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(">>> Анализ опубликован.")

if __name__ == "__main__":
    run_analysis()
