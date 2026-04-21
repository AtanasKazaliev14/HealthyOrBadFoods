import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re
import cv2

# ===============================
# Load OCR Reader
# ===============================
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

reader = load_reader()

# ===============================
# Harmful E-numbers Dictionary
# ===============================
UNHEALTHY_E_NUMBERS = {
    "E620": {
        "en": "Monosodium glutamate (MSG)",
        "bg": "Мононатриев глутамат"
    },
    "E621": {
        "en": "MSG variant",
        "bg": "Вариант на мононатриев глутамат"
    },
    "E627": {
        "en": "Disodium guanylate",
        "bg": "Динатриев гуанилат"
    },
    "E631": {
        "en": "Disodium inosinate",
        "bg": "Динатриев инозинат"
    },
    "E950": {
        "en": "Acesulfame K",
        "bg": "Ацесулфам К"
    },
    "E951": {
        "en": "Aspartame",
        "bg": "Аспартам"
    },
    "E952": {
        "en": "Cyclamate",
        "bg": "Цикламат"
    },
    "E954": {
        "en": "Saccharin",
        "bg": "Захарин"
    }
}

# ===============================
# Image Preprocessing
# ===============================
def preprocess_image(image):
    img_array = np.array(image)

    # Convert to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # Blur for better OCR
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold for clearer text
    _, thresh = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return thresh

# ===============================
# Normalize OCR Mistakes
# ===============================
def normalize_e_number(e):
    e = e.upper()
    e = e.replace(" ", "")
    e = e.replace("-", "")
    e = e.replace(".", "")

    # Common OCR corrections
    e = e.replace("O", "0")
    e = e.replace("I", "1")
    e = e.replace("Z", "2")

    return e

# ===============================
# Extract E-numbers
# ===============================
def detect_e_numbers(text):
    raw_matches = re.findall(r'[Ee][\s\-\.]?\d{3}', text)

    normalized = [normalize_e_number(e) for e in raw_matches]

    return list(set(normalized))

# ===============================
# Streamlit UI
# ===============================
st.title("🧪 Ingredient Scanner (E-number Detector)")
st.write(
    "Upload an image of ingredients. The app will detect harmful additives "
    "and show their names in English and Bulgarian."
)

uploaded_file = st.file_uploader(
    "📤 Upload an image",
    type=["jpg", "png", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)

    st.image(image, caption="📷 Uploaded Image", use_column_width=True)

    st.write("🔍 Processing image and extracting text...")

    processed_image = preprocess_image(image)

    # OCR
    results = reader.readtext(processed_image, detail=0)

    extracted_text = " ".join(results)

    st.subheader("📄 Extracted Text")
    st.write(extracted_text)

    # Detect E-numbers
    found_e_numbers = detect_e_numbers(extracted_text)

    st.subheader("📊 Detected E-numbers")

    if found_e_numbers:
        st.write(", ".join(found_e_numbers))
    else:
        st.info("No E-numbers detected.")

    # Check harmful ones
    st.subheader("⚠️ Harmful Additives Check")

    found_unhealthy = []

    for e in found_e_numbers:
        if e in UNHEALTHY_E_NUMBERS:
            found_unhealthy.append(e)

    if found_unhealthy:
        st.error("🚨 Harmful additives detected!")

        for e in found_unhealthy:
            st.markdown(
                f"**{e}** → "
                f"{UNHEALTHY_E_NUMBERS[e]['en']} "
                f"(**{UNHEALTHY_E_NUMBERS[e]['bg']}**)"
            )
    else:
        if found_e_numbers:
            st.success("✅ No known harmful E-numbers detected.")
