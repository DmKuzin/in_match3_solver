# solve_post.py
import requests
import json


# Функция для выполнения POST-запроса
def get_next_move(grid_board, api_key="f91d8f74-61f3-4d3b-9b95-e4268d0e9f4e", mode="gather", is_easy_fight=True):
    url = "http://91.197.98.134:5000/get-next-move"
    headers = {"Content-Type": "application/json"}

    # Подготовка данных для запроса
    data = {
        "api_key": api_key,
        "grid": grid_board,
        "mode": mode,
        "is_easy_fight": is_easy_fight
    }

    # Отправка POST-запроса
    response = requests.post(url, headers=headers, json=data)

    # Обработка ответа
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Ошибка {response.status_code}: {response.text}"}
