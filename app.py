import streamlit as st
from rembg import remove
from PIL import Image
import numpy as np
import io
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(layout="wide")

st.title("🎯 Click to Change Object Color")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Load image
    input_image = Image.open(uploaded_file).convert("RGBA")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Click on area to change")

        # Remove background
        output_image = remove(input_image).convert("RGBA")

        # Resize for stability
        output_image = output_image.resize((600, 600))

        img_array = np.array(output_image)

        # CLICK detection
        coords = streamlit_image_coordinates(output_image)

    # Color picker
    new_color = st.color_picker("Pick New Color", "#FF0000")

    # Tolerance slider (important)
    tolerance = st.slider("Color Similarity", 10, 100, 40)

    if coords is not None:
        x, y = coords["x"], coords["y"]

        st.write(f"📍 Selected pixel: ({x}, {y})")

        # Get selected pixel color
        selected_color = img_array[y, x][:3]

        # Convert HEX → RGB
        new_color_rgb = tuple(int(new_color[i:i+2], 16) for i in (1, 3, 5))

        # Compute color distance
        diff = np.linalg.norm(img_array[:, :, :3] - selected_color, axis=2)

        mask = diff < tolerance

        result = img_array.copy()
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

else:
    st.info("👆 Upload an image to start")
