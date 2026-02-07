def generate_site(matches_results):
    """
    matches_results: список словарей с данными по всем играм дня
    """
    cards_html = ""
    
    for match in matches_results:
        cards_html += f"""
        <div class="card">
            <div class="teams">
                <span>{match['away_team']}</span>
                <span class="vs">VS</span>
                <span>{match['home_team']}</span>
            </div>
            <div class="prediction-bar">
                <div class="bar-home" style="width: {match['prob_home']}%"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.9em;">
                <span>{match['prob_away']}%</span>
                <span>{match['prob_home']}% (Дом)</span>
            </div>
            <div class="stats-box">
                <b>Анализ ИИ:</b> {match['insight']}<br>
                <span class="badge">Back-to-Back: {match['fatigue']}</span>
                <span class="badge">Mood: {match['mood']}</span>
            </div>
        </div>
        """

    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Вставляем все карточки сразу
    new_html = html.replace('', cards_html)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

print("Генератор сайта настроен на обработку всей лиги!")
