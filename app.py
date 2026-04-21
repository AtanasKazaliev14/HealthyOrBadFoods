import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re
import cv2


# Load OCR

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

reader = load_reader()

# Database of Ingredients

UNHEALTHY_DATABASE = {
    # E-numbers
    "E620": {"en": "Monosodium glutamate", "bg": "Мононатриев глутамат", "risk": 2},
    "E621": {"en": "MSG", "bg": "Мононатриев глутамат", "risk": 2},
    "E627": {"en": "Disodium guanylate", "bg": "Динатриев гуанилат", "risk": 2},
    "E631": {"en": "Disodium inosinate", "bg": "Динатриев инозинат", "risk": 2},
    "E950": {"en": "Acesulfame K", "bg": "Ацесулфам К", "risk": 3},
    "E951": {"en": "Aspartame", "bg": "Аспартам", "risk": 3},
    "E952": {"en": "Cyclamate", "bg": "Цикламат", "risk": 3},
    "E954": {"en": "Saccharin", "bg": "Захарин", "risk": 3},

    # Text ingredients
    "caffeine": {"en": "Caffeine", "bg": "Кофеин", "risk": 2},
    "taurine": {"en": "Taurine", "bg": "Таурин", "risk": 1},
    "sucralose": {"en": "Sucralose", "bg": "Сукралоза", "risk": 3},
    "acesulfame k": {"en": "Acesulfame K", "bg": "Ацесулфам К", "risk": 3},
    "aspartame": {"en": "Aspartame", "bg": "Аспартам", "risk": 3},
    "benzoic acid": {"en": "Benzoic acid", "bg": "Бензоена киселина", "risk": 2},
    "sorbic acid": {"en": "Sorbic acid", "bg": "Сорбинова киселина", "risk": 1},
    "glucuronolactone": {"en": "Glucuronolactone", "bg": "Глюкуронолактон", "risk": 1},
    "inositol": {"en": "Inositol", "bg": "Инозитол", "risk": 1},
    "ginseng": {"en": "Ginseng", "bg": "Женшен", "risk": 1},
    "guarana": {"en": "Guarana", "bg": "Гуарана", "risk": 2}
}
# Image preprocessing
def preprocess_image(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

# ===============================
# Normalize OCR mistakes
# ===============================
def normalize_e_number(e):
    e = e.upper()
    e = e.replace(" ", "").replace("-", "").replace(".", "")
    e = e.replace("O", "0").replace("I", "1").replace("Z", "2")
    return e

# Detect everything

def detect_all(text):
    text_lower = text.lower()
    found = []

    # Detect E-numbers
    e_matches = re.findall(r'[Ee][\s\-\.]?\d{3}', text)
    for e in e_matches:
        e_clean = normalize_e_number(e)
        if e_clean in UNHEALTHY_DATABASE:
            found.append(e_clean)

    # Detect text ingredients
    for key in UNHEALTHY_DATABASE:
        if not key.startswith("E"):
            if key in text_lower:
                found.append(key)

    return list(set(found))

# Scoring system

def calculate_score(found_items):
    return sum(UNHEALTHY_DATABASE[item]["risk"] for item in found_items)

def get_health_label(score):
    if score == 0:
        return "🟢 Healthy"
    elif score <= 3:
        return "🟡 Moderate"
    else:
        return "🔴 Unhealthy"

# ===============================
# UI
# ===============================
st.title("🧪 AI Ingredient Scanner")
st.write("Scan ingredients and detect potentially harmful substances.")

uploaded_file = st.file_uploader("📤 Upload image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    st.write("🔍 Processing...")

    processed = preprocess_image(image)

    results = reader.readtext(processed, detail=0)
    extracted_text = " ".join(results)

    st.subheader("📄 Extracted Text")
    st.write(extracted_text)

    found_items = detect_all(extracted_text)

    st.subheader("🧪 Analysis")

    if found_items:
        score = calculate_score(found_items)
        label = get_health_label(score)

        st.markdown(f"### {label} (Score: {score})")

        for item in found_items:
            data = UNHEALTHY_DATABASE[item]
            st.markdown(
                f"**{data['en']}** ({data['bg']}) → Risk: {data['risk']}"
            )
    else:
        st.success("✅ No risky ingredients detected.")
