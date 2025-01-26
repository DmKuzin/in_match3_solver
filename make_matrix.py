import numpy as np

def detect_images_in_grid(res, confidence_threshold=0.85):
    # Маппинг имён классов на аббревиатуры
    class_mapping = {
        'square': 'g',  # 'g' для 'square'
        'triangle_up': 'r',  # 'r' для 'triangle_up'
        'triangle_down': 'p',  # 'p' для 'triangle_down'
        'circle': 'b',  # 'b' для 'circle'
        'pentagon': 'y'  # 'y' для 'pentagon'
    }

    # Ожидаемые классы (class_names)
    object_classes = ['circle', 'pentagon', 'square', 'triangle_down', 'triangle_up']

    # Получаем результат из модели (res) - предполагаем, что это результат работы YOLOv8
    # Пример структуры: res.xywh (координаты bbox), res.cls (идентификаторы классов), res.conf (confidence)

    bbox_list = []  # Список для координат bbox
    class_names_list = []  # Список для имен классов
    confidence_list = []  # Список для уверенности (confidence)

    for result in res:
        for box in result.boxes:
            bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
            confidence = box.conf[0].item()  # confidence
            class_id = box.cls[0].item()  # class_id
            class_name = result.names[class_id]  # имя класса

            # Добавляем данные в списки
            bbox_list.append(bbox)
            class_names_list.append(class_name)
            confidence_list.append(confidence)

    # Инициализируем пустую матрицу 6x6
    grid = np.full((6, 6), None)  # Заполняем None, если нет объектов

    # Находим рамку 'board'
    board_bbox = None
    for i, class_name in enumerate(class_names_list):
        if class_name == 'board':  # Ищем рамку
            board_bbox = bbox_list[i]
            break

    if board_bbox is None:
        raise ValueError("Рамка (board) не найдена в результатах детекции!")

    # Получаем координаты рамки 'board'
    board_x1, board_y1, board_x2, board_y2 = board_bbox

    # Проверяем, что рамка 'board' корректно задана
    if board_x1 >= board_x2 or board_y1 >= board_y2:
        raise ValueError("Рамка (board) имеет некорректные координаты!")

    # Заполняем матрицу grid для объектов, находящихся внутри рамки
    for i, (bbox, class_name, confidence) in enumerate(zip(bbox_list, class_names_list, confidence_list)):
        if class_name == 'board' or confidence < confidence_threshold:
            continue  # Пропускаем 'board' и объекты с низким confidence

        # Проверяем, что объект находится внутри рамки 'board'
        x1, y1, x2, y2 = bbox
        if x1 < board_x1 or y1 < board_y1 or x2 > board_x2 or y2 > board_y2:
            continue  # Если объект выходит за рамки, пропускаем его

        # Находим центр объекта, чтобы определить его позицию в сетке 6x6
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        # Рассчитываем индекс в сетке 6x6
        grid_x = int((center_x - board_x1) / (board_x2 - board_x1) * 6)
        grid_y = int((center_y - board_y1) / (board_y2 - board_y1) * 6)

        # Ограничиваем индексы сетки от 0 до 5
        grid_x = min(max(grid_x, 0), 5)
        grid_y = min(max(grid_y, 0), 5)

        # Записываем аббревиатуру класса в соответствующую ячейку матрицы
        if class_name in class_mapping:
            grid[grid_y, grid_x] = class_mapping[class_name]

    return str(grid)