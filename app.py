# Python In-built packages
from pathlib import Path
import PIL

# External packages
import streamlit as st

# Local Modules
import settings
import helper

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

# # Model Options
# model_type = st.sidebar.radio(
#     "Select Task", ['Detection', 'Segmentation'])

confidence = float(st.sidebar.slider(
    "Select Model Confidence", 25, 100, 40)) / 100

# Get trained model path
model_path = Path(settings.DETECTION_MODEL)
# Selecting Detection Or Segmentation
# if model_type == 'Detection':
#     model_path = Path(settings.DETECTION_MODEL)
# elif model_type == 'Segmentation':
#     model_path = Path(settings.SEGMENTATION_MODEL)

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

    col1, col2, col3 = st.columns([0.5, 0.5, 0.5])  # 50% ширины для каждой колонки

    # Контейнер для первой колонки с исходным изображением
    with col1:
        with st.container(height=500):  # Высота в пикселях
            st.write("Source image")
            try:
                if source_img is None:
                    default_image_path = str(settings.DEFAULT_IMAGE)
                    default_image = PIL.Image.open(default_image_path)
                    st.image(default_image_path, caption="Default Image", width=300)  # Ограничиваем ширину
                else:
                    uploaded_image = PIL.Image.open(source_img)
                    st.image(source_img, caption="Uploaded Image", width=300)  # Ограничиваем ширину
            except Exception as ex:
                st.error("Error occurred while opening the image.")
                st.error(ex)

    # Проверка нажатия кнопки "Detect Objects"
    if st.sidebar.button('Detect Objects', key="detect_objects"):
        if source_img is None:
            st.write("No image uploaded for detection.")
        else:
            # Проводим детекцию на изображении
            res = model.predict(uploaded_image, conf=confidence)
            boxes = res[0].boxes
            res_plotted = res[0].plot()[:, :, ::-1]

            # Контейнер для второй колонки с результатом детекции
            with col2:
                with st.container(height=500):
                    st.write("Detected image")
                    st.image(res_plotted, caption='Detected Image', width=300)  # Ограничиваем ширину
                    # Отображаем детекционные результаты как текст
                    st.write("Detection Results:")
                    for box in boxes:
                        st.write(f"Class: {box.cls}, Confidence: {box.conf}, Coordinates: {box.xyxy}")

            # Контейнер для третьей колонки с результатом детекции
            with col3:
                with st.container(height=500):
                    st.write("Detected image in col3")
                    st.image(res_plotted, caption='Detected Image', width=300)  # Ограничиваем ширину
                    # Отображаем детекционные результаты как текст
                    st.write("Detection Results in col3:")
                    for box in boxes:
                        st.write(f"Class: {box.cls}, Confidence: {box.conf}, Coordinates: {box.xyxy}")

    else:
        with col2:
            with st.container(height=500):
                st.write("Detected image")
        with col3:
            with st.container(height=500):
                st.write("Detected image in col3")

elif source_radio == settings.VIDEO:
    helper.play_stored_video(confidence, model)

elif source_radio == settings.WEBCAM:
    helper.play_webcam(confidence, model)

# elif source_radio == settings.RTSP:
#     helper.play_rtsp_stream(confidence, model)
#
# elif source_radio == settings.YOUTUBE:
#     helper.play_youtube_video(confidence, model)

else:
    st.error("Please select a valid source type!")
