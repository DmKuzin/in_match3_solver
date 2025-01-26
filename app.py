# Python In-built packages
from pathlib import Path
import PIL

# External packages
import streamlit as st

# Local Modules
import settings
import helper
import make_matrix
import solve_post

# Setting page layout
st.set_page_config(
    page_title="in match3 solver",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page heading
st.title("in match3 solver")

# Sidebar
st.sidebar.header("ML Model Config")

confidence = float(st.sidebar.slider(
    "Select Model Confidence", 25, 100, 40)) / 100

# Get trained model path
model_path = Path(settings.DETECTION_MODEL)

# Load Pre-trained ML Model
try:
    model = helper.load_model(model_path)
except Exception as ex:
    st.error(f"Unable to load model. Check the specified path: {model_path}")
    st.error(ex)

st.sidebar.header("Image/Video Config")
source_radio = st.sidebar.radio(
    "Select Source", settings.SOURCES_LIST)

source_img = None
# If image is selected
if source_radio == settings.IMAGE:
    source_img = st.sidebar.file_uploader(
        "Choose an image...", type=("jpg", "jpeg", "png", 'bmp', 'webp'))

    col1, col2, col3 = st.columns([0.5, 0.5, 0.5], gap="medium")  # 50% ширины для каждой колонки

    # Контейнер для первой колонки с исходным изображением
    with col1:
        with st.container(height=settings.CONTAINER_HEIGHT):  # Высота в пикселях
            st.write("Source image")
            try:
                # Если изображение загружено
                if source_img is not None:
                    uploaded_image = PIL.Image.open(source_img)
                    st.image(source_img, caption="Uploaded Image", width=settings.IMAGE_WIDTH)  # Ограничиваем ширину
                else:
                    # Если изображение не загружено, показываем изображение по умолчанию
                    default_image_path = str(settings.DEFAULT_IMAGE)
                    default_image = PIL.Image.open(default_image_path)
                    st.image(default_image_path, caption="Default Image", width=settings.IMAGE_WIDTH)  # Ограничиваем ширину
                    uploaded_image = default_image  # Устанавливаем default_image как входное изображение
            except Exception as ex:
                st.error("Error occurred while opening the image.")
                st.error(ex)

    # Проверка нажатия кнопки "Detect Objects"
    if st.sidebar.button('Detect Objects', key="detect_objects"):
        if uploaded_image is None:
            st.write("No image uploaded for detection.")
        else:
            # Проводим детекцию на изображении
            res = model.predict(uploaded_image, conf=confidence)
            boxes = res[0].boxes
            res_plotted = res[0].plot()[:, :, ::-1]

            # Контейнер для второй колонки с результатом детекции
            with col2:
                with st.container(height=settings.CONTAINER_HEIGHT):
                    st.write("Detected image")
                    st.image(res_plotted, caption='Detected Image', width=settings.IMAGE_WIDTH)  # Ограничиваем ширину

                    # Результаты в выпадающем меню
                    with st.expander("Detection Results"):
                        for box in boxes:
                            class_id = int(box.cls)  # Номер класса
                            class_name = model.names[class_id]  # Имя класса
                            st.write(f"Class: {class_name}, Confidence: {box.conf}, Coordinates: {box.xyxy}")

            # Контейнер для третьей колонки с результатом детекции
            with col3:
                with st.container(height=settings.CONTAINER_HEIGHT):
                    st.write("Result matrix")
                    # Вызываем функцию detect_images_in_grid для создания матрицы
                    grid_board = make_matrix.detect_images_in_grid(res, confidence_threshold=0.5)
                    st.text(grid_board)

                    # Вызываем функцию solve с передачей grid_board
                    st.write("Requesting next move...")
                    result = solve_post.get_next_move(grid_board)  # Вызов функции solve с переданным grid_board

                    # Отображаем результат от функции solve
                    st.subheader("Ответ от сервера:")
                    st.text(result)
    else:
        with col2:
            with st.container(height=settings.CONTAINER_HEIGHT):
                st.write("Detected image")
        with col3:
            with st.container(height=settings.CONTAINER_HEIGHT):
                st.write("Detected image in col3")

elif source_radio == settings.VIDEO:
    helper.play_stored_video(confidence, model)

elif source_radio == settings.WEBCAM:
    helper.play_webcam(confidence, model)

else:
    st.error("Please select a valid source type!")
