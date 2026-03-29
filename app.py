import streamlit as st
from rembg import remove
from PIL import Image
import numpy as np
import io
from streamlit_drawable_canvas import st_canvas

st.set_page_config(layout="wide")

st.title("🎯 AI Background + Object Color Changer")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Load image
    input_image = Image.open(uploaded_file).convert("RGBA")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(input_image, use_column_width=True)

    # Remove background
    with st.spinner("Removing background..."):
        output_image = remove(input_image)

    # Convert to numpy
    img_array = np.array(output_image)

    st.subheader("🖌️ Draw on object to change color")

    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=15,
        stroke_color="#FF0000",
        background_image=output_image,
        update_streamlit=True,
        height=output_image.height,
        width=output_image.width,
        drawing_mode="freedraw",
        key="canvas",
    )

    # Color picker
    new_color = st.color_picker("Pick Object Color", "#00FF00")

    if canvas_result.image_data is not None:
        mask = canvas_result.image_data[:, :, 3] > 0

        # Convert HEX → RGB
        new_color_rgb = tuple(int(new_color[i:i+2], 16) for i in (1, 3, 5))

        result = img_array.copy()

        # Apply color only to selected region
        result[mask] = (*new_color_rgb, 255)

        final_image = Image.fromarray(result)

        with col2:
            st.subheader("Edited Image")
            st.image(final_image, use_column_width=True)

        # Download
        buf = io.BytesIO()
        final_image.save(buf, format="PNG")

        st.download_button(
            "⬇️ Download Image",
            buf.getvalue(),
            file_name="edited.png",
            mime="image/png"
        )