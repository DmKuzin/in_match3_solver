# solve_post.py
import requests
import json


# Функция для выполнения POST-запроса
def get_next_move(grid_board, mode="gather", is_easy_fight=True):
    api_key = "f91d8f74-61f3-4d3b-9b95-e4268d0e9f4e"
    url = "http://91.197.98.134:5000/get-next-move"
    headers = {"Content-Type": "application/json"}

    # Преобразуем введенный грид в список
    grid_data_list = grid_board.tolist()
    is_easy_fight_bin = bool(is_easy_fight)
    # Подготовка данных для запроса
    data = {
        "api_key": api_key,
        "grid": grid_data_list,
        "mode": mode,
        "is_easy_fight": is_easy_fight_bin
    }

    # Отправка POST-запроса
    response = requests.post(url, headers=headers, json=data)

    # Обработка ответа
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Ошибка {response.status_code}: {response.text}"}
