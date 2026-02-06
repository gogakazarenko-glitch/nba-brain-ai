import pandas as pd
import numpy as np

def prepare_match_vector(team_a_stats, team_b_stats, team_a_news, team_b_news):
    """
    Превращает все данные о матче в один вектор (набор чисел) для нейронки.
    """
    # Собираем Hard Stats (Очки, Подборы, Передачи)
    # Собираем Physical Data (Средний рост, вес, размах рук пятерки)
    # Добавляем Коэффициент Усталости (1.0 - свежие, 0.7 - back-to-back)
    
    match_features = []
    
    # Данные Команды А
    match_features.extend(team_a_stats) # например, [110.5, 45.2, 25.1]
    match_features.append(team_a_news)  # Психологический скор (от 0.1 до 1.0)
    
    # Данные Команды Б
    match_features.extend(team_b_stats)
    match_features.append(team_b_news)
    
    # Превращаем в формат, понятный PyTorch (тензор)
    return np.array(match_features, dtype=np.float32)

# Пример того, как будет выглядеть одна строка данных для обучения:
# [ОчкиА, ПодборыА, РостА, МотивацияА, ОчкиБ, ПодборыБ, РостБ, МотивацияБ] -> Итог (1 или 0)

def create_training_set(history_games):
    dataset = []
    for game in history_games:
        vector = prepare_match_vector(game['stats_a'], game['stats_b'], game['mood_a'], game['mood_b'])
        target = game['winner'] # 1 если выиграла Команда А, 0 если Б
        dataset.append((vector, target))
    return dataset

print("Конвейер данных готов к работе!")