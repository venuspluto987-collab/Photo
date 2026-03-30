import streamlit as st
import numpy as np
from PIL import Image
import io
import torch
from segment_anything import sam_model_registry, SamPredictor
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(layout="wide")

st.title("🔥 AI Click → Select Object → Change Color")

# Load SAM model
@st.cache_resource
def load_model():
    sam = sam_model_registry["vit_b"](checkpoint="sam_vit_b.pth")
    sam.to(device="cpu")
    predictor = SamPredictor(sam)
    return predictor

predictor = load_model()

uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image = image.resize((600, 600))
    img_np = np.array(image)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👆 Click on object")
        coords = streamlit_image_coordinates(image)

    predictor.set_image(img_np)

    new_color = st.color_picker("Pick Color", "#FF0000")
    new_color_rgb = tuple(int(new_color[i:i+2], 16) for i in (1, 3, 5))

    if coords is not None:
        x, y = coords["x"], coords["y"]

        st.write(f"📍 Clicked: ({x}, {y})")

        input_point = np.array([[x, y]])
        input_label = np.array([1])

        masks, scores, _ = predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True,
        )

        # 🔥 Pick BEST mask (IMPORTANT FIX)
        best_mask = masks[np.argmax(scores)]

        # Show mask preview (DEBUG)
        st.subheader("🧠 Detected Mask")
        st.image(best_mask.astype("uint8") * 255)

        # Apply color
        result = img_np.copy()
        result[best_mask] = new_color_rgb

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
            file_name="ai_edit.png",
            mime="image/png"
        )

else:
    st.info("Upload image to start")
