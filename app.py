import streamlit as st
from rembg import remove
from PIL import Image
import numpy as np
import io

st.set_page_config(layout="wide")

st.title("🎯 Full Object Color Changer")

uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    input_image = Image.open(uploaded_file).convert("RGBA")

    col1, col2 = st.columns(2)

    with col1:
        st.image(input_image, caption="Original Image", use_column_width=True)

    # Remove background (this gives clean object mask)
    output_image = remove(input_image).convert("RGBA")

    img_array = np.array(output_image)

    # Extract mask (alpha channel)
    mask = img_array[:, :, 3] > 0

    # Pick color
    new_color = st.color_picker("Pick Object Color", "#FF0000")
    new_color_rgb = tuple(int(new_color[i:i+2], 16) for i in (1, 3, 5))

    result = img_array.copy()

    # Apply color ONLY to object
    result[mask] = (*new_color_rgb, 255)

    final_image = Image.fromarray(result)

    with col2:
        st.image(final_image, caption="Full Object Changed", use_column_width=True)

    # Download
    buf = io.BytesIO()
    final_image.save(buf, format="PNG")

    st.download_button(
        "⬇️ Download",
        buf.getvalue(),
        file_name="edited.png",
        mime="image/png"
    )
