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

logo = settings.APP_LOGO_PATH

# Setting page layout
st.set_page_config(
    page_title="in match3 solver",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page heading
#st.title("in match3 solver")

# Sidebar
st.sidebar.markdown('<h1 style="text-align: center;">-- IN MATCH 3 --</h1>', unsafe_allow_html=True)
st.sidebar.image(logo, width=150)

st.sidebar.header("ML Model Config")
model_confidence = float(st.sidebar.slider(
    "Select Model Confidence", 25, 100, 40)) / 100

matrix_confidence = float(st.sidebar.slider(
    "Select Result matrix Confidence", 25, 100, 40)) / 100

st.sidebar.header("Solver config")
strategy_mode = st.sidebar.radio(
    "Strategy mode", settings.STRATEGY_MOD_LIST)

fight_mode = st.sidebar.radio(
    "Is easy fight", settings.FIGHT_MOD_LIST)

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
        #with st.container(height=settings.CONTAINER_HEIGHT):  # Высота в пикселях
        with st.container(height=None, border=True):  # Высота в пикселях
            st.write("Source image")
            try:
                # Если изображение загружено
                if source_img is not None:
                    uploaded_image = PIL.Image.open(source_img)
                    st.image(source_img, caption=None, width=settings.IMAGE_WIDTH)  # Ограничиваем ширину
                else:
                    # Если изображение не загружено, показываем изображение по умолчанию
                    default_image_path = str(settings.DEFAULT_IMAGE)
                    default_image = PIL.Image.open(default_image_path)
                    st.image(default_image_path, caption=None, width=settings.IMAGE_WIDTH)  # Ограничиваем ширину
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
            res = model.predict(uploaded_image, conf=model_confidence)
            boxes = res[0].boxes
            res_plotted = res[0].plot()[:, :, ::-1]

            # Контейнер для второй колонки с результатом детекции
            with col2:
                #with st.container(height=settings.CONTAINER_HEIGHT):
                with st.container(height=None, border=True):  # Высота в пикселях
                    st.write("Detected image")
                    st.image(res_plotted, caption=None, width=settings.IMAGE_WIDTH)  # Ограничиваем ширину

                    # Результаты в выпадающем меню
                    with st.expander("Detection Results"):
                        for box in boxes:
                            class_id = int(box.cls)  # Номер класса
                            class_name = model.names[class_id]  # Имя класса
                            st.write(f"Class: {class_name}, Confidence: {box.conf}, Coordinates: {box.xyxy}")

            # Контейнер для третьей колонки с результатом детекции
            with col3:
                #with st.container(height=settings.CONTAINER_HEIGHT):
                with st.container(height=None, border=True):  # Высота в пикселях
                    st.write("Result matrix")
                    # Вызываем функцию detect_images_in_grid для создания матрицы
                    grid_board = make_matrix.detect_images_in_grid(res, confidence_threshold=matrix_confidence)
                    st.text(grid_board)

                    # Вызываем функцию solve с передачей grid_board
                    st.write("Requesting next move...")

                    result = solve_post.get_next_move(grid_board, mode=strategy_mode, is_easy_fight=fight_mode)  # Вызов функции solve с переданным grid_board

                    # Отображаем результат от функции solve
                    st.subheader("Ответ от сервера:")
                    st.text(result)
    else:
        with col2:
            #with st.container(height=settings.CONTAINER_HEIGHT):
            with st.container(height=None, border=True):  # Высота в пикселях
                st.write("Detected image")
        with col3:
            #with st.container(height=settings.CONTAINER_HEIGHT):
            with st.container(height=None, border=True):  # Высота в пикселях
                st.write("Result matrix")

elif source_radio == settings.VIDEO:
    helper.play_stored_video(model_confidence, model)

elif source_radio == settings.WEBCAM:
    helper.play_webcam(model_confidence, model)

else:
    st.error("Please select a valid source type!")
