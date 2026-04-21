import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re

# Initialize OCR reader
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

reader = load_reader()

st.title("🧪 Ingredient Scanner (E-number Detector)")

st.write("Upload an image of ingredients. The app will detect harmful additives like E620.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

# Example list of "unhealthy" E-numbers
UNHEALTHY_E_NUMBERS = {
    "E620": "Monosodium glutamate (MSG)",
    "E621": "MSG variant",
    "E627": "Disodium guanylate",
    "E631": "Disodium inosinate",
    "E950": "Acesulfame K",
    "E951": "Aspartame",
    "E952": "Cyclamate",
    "E954": "Saccharin"
}

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert to numpy array
    img_array = np.array(image)

    st.write("🔍 Extracting text...")

    results = reader.readtext(img_array, detail=0)
    extracted_text = " ".join(results)

    st.subheader("📄 Extracted Text")
    st.write(extracted_text)

    # Find E-numbers using regex
    found_e_numbers = re.findall(r'\b[Ee]\s?\d{3}\b', extracted_text)

    # Normalize format (E620 instead of e 620)
    found_e_numbers = [e.replace(" ", "").upper() for e in found_e_numbers]

    st.subheader("⚠️ Detected Additives")

    found_unhealthy = []

    if found_e_numbers:
        for e in set(found_e_numbers):
            if e in UNHEALTHY_E_NUMBERS:
                found_unhealthy.append((e, UNHEALTHY_E_NUMBERS[e]))

        if found_unhealthy:
            st.error("🚨 Unhealthy ingredients found!")
            for e, desc in found_unhealthy:
                st.write(f"{e} → {desc}")
        else:
            st.success("✅ No known harmful E-numbers detected.")
            st.write("Detected E-numbers:", ", ".join(set(found_e_numbers)))
    else:
        st.info("No E-numbers detected.")
