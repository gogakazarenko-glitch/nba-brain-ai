import requests
from bs4 import BeautifulSoup

def check_player_status(player_name):
    # Мы будем использовать поиск по спортивным новостям (например, через RSS или Google News)
    # Для примера возьмем упрощенный поиск по заголовкам
    query = f"{player_name} NBA injury status news"
    url = f"https://www.google.com/search?q={query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Ключевые слова, которые "пугают" нейронку
    negative_triggers = ['out', 'injury', 'doubtful', 'personal reasons', 'rest', 'miss']
    
    text = soup.get_text().lower()
    
    status_score = 1.0 # По умолчанию игрок в порядке
    
    for word in negative_triggers:
        if word in text:
            print(f"Внимание! Найдено негативное слово для {player_name}: {word}")
            status_score = 0.5 # Снижаем "вес" игрока для нейронки в два раза
            break
            
    return status_score

# Пример проверки
# print(f"Коэффициент готовности: {check_player_status('LeBron James')}")