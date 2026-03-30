import streamlit as st
from rembg import remove
from PIL import Image
import numpy as np
import io
from streamlit_image_coordinates import streamlit_image_coordinates
from collections import deque

st.set_page_config(layout="wide")

st.title("🎯 Smart Click → Select Area → Change Color")

uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    input_image = Image.open(uploaded_file).convert("RGBA")

    # Remove background
    output_image = remove(input_image).convert("RGBA")
    output_image = output_image.resize((600, 600))

    img_array = np.array(output_image)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👆 Click on object")
        coords = streamlit_image_coordinates(output_image)

    # Controls
    new_color = st.color_picker("Pick Color", "#FF0000")
    tolerance = st.slider("Selection Sensitivity", 10, 80, 30)

    if coords is not None:
        x, y = coords["x"], coords["y"]
        st.write(f"📍 Clicked: ({x}, {y})")

        selected_color = img_array[y, x][:3]

        h, w, _ = img_array.shape
        visited = np.zeros((h, w), dtype=bool)
        mask = np.zeros((h, w), dtype=bool)

        # BFS (region growing)
        queue = deque()
        queue.append((y, x))
        visited[y, x] = True

        while queue:
            cy, cx = queue.popleft()

            current_color = img_array[cy, cx][:3]
            diff = np.linalg.norm(current_color - selected_color)

            if diff < tolerance:
                mask[cy, cx] = True

                for ny, nx in [(cy+1, cx), (cy-1, cx), (cy, cx+1), (cy, cx-1)]:
                    if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                        visited[ny, nx] = True
                        queue.append((ny, nx))

        # Convert HEX → RGB
        new_color_rgb = tuple(int(new_color[i:i+2], 16) for i in (1, 3, 5))

        result = img_array.copy()
        result[mask] = (*new_color_rgb, 255)

        final_image = Image.fromarray(result)

        with col2:
            st.subheader("🎨 Edited Image")
            st.image(final_image, use_column_width=True)

        # Download
        buf = io.BytesIO()
        final_image.save(buf, format="PNG")

        st.download_button(
            "⬇️ Download",
            buf.getvalue(),
            file_name="edited.png",
            mime="image/png"
        )

else:
    st.info("Upload an image to start")
    
