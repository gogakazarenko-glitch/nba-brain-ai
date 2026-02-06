import torch
from brain import NBABrain
from data_integrator import prepare_match_vector
import numpy as np

def predict_today():
    # 1. Загружаем обученную нейронку
    input_size = 100 # Должно совпадать с тем, что было при обучении
    model = NBABrain(input_size)
    model.load_state_dict(torch.load('nba_model_2026.pth'))
    model.eval() # Переводим в режим предсказания

    print("--- NBA AI PREDICTOR 2026 ---")
    print("Загрузка актуальных данных: травмы, усталость, личные встречи...")

    # 2. Имитируем получение данных на сегодняшний матч
    # В реальности тут вызываются твои функции:
    # team_a_stats = get_current_stats('Lakers')
    # team_a_mood = check_player_status('LeBron James') 
    
    # Пример данных для матча (вектор из 100 чисел)
    # Здесь нейронка учитывает: [Рост, Вес, Усталость, Новости, Лички...]
    mock_match_data = torch.randn(1, input_size) 

    # 3. Делаем прогноз
    with torch.no_grad():
        prediction = model(mock_match_data)
        prob_a = prediction[0][0].item() * 100
        prob_b = prediction[0][1].item() * 100

    print(f"\nМатч: Команда А vs Команда Б")
    print(f"Вероятность победы Команды А: {prob_a:.2f}%")
    print(f"Вероятность победы Команды Б: {prob_b:.2f}%")
    
    if prob_a > prob_b:
        print("Рекомендация: Ставка на Команду А")
    else:
        print("Рекомендация: Ставка на Команду Б")

if __name__ == "__main__":
    predict_today()