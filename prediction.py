import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# Load model dan data referensi
model = joblib.load("model.joblib")
df = pd.read_csv("data_cleaned.csv")

# Setup encoder dan scaler
X = df.drop(columns=["Status"])
y = df["Status"]

le_status = LabelEncoder()
le_status.fit(y)

categorical_cols = X.select_dtypes(include='object').columns.tolist()
numerical_cols = X.select_dtypes(include=np.number).columns.tolist()

# Label encoding kategorikal
encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    le.fit(df[col])
    encoders[col] = le

# Scaling numerik
scaler = MinMaxScaler()
scaled_X = X.copy()
for col in categorical_cols:
    scaled_X[col] = encoders[col].transform(X[col])
scaler.fit(scaled_X[numerical_cols])

# === Streamlit UI ===
st.set_page_config(page_title="Prediksi Mahasiswa", layout="centered")
st.markdown("<h2 style='text-align:center;'>🎓 Prediksi Status Mahasiswa</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Masukkan data berikut untuk mengetahui apakah mahasiswa akan lulus atau drop out.</p>", unsafe_allow_html=True)
st.write("---")

# Layout input
with st.form("form_prediksi"):
    col1, col2 = st.columns(2)
    input_data = {}

    # Input kategori (dropdown)
    with col1:
        for col in categorical_cols[:len(categorical_cols)//2]:
            options = sorted(df[col].dropna().unique())
            input_data[col] = st.selectbox(f"{col}", options)

    with col2:
        for col in categorical_cols[len(categorical_cols)//2:]:
            options = sorted(df[col].dropna().unique())
            input_data[col] = st.selectbox(f"{col}", options)

    # Input numerik (angka)
    for col in numerical_cols:
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        median_val = float(df[col].median())
        input_data[col] = st.number_input(f"{col}", min_value=min_val, max_value=max_val, value=median_val)

    submitted = st.form_submit_button("🔍 Prediksi")

if submitted:
    try:
        # Buat DataFrame dari input
        input_df = pd.DataFrame([input_data])

        # Encode kategorikal
        for col in categorical_cols:
            input_df[col] = encoders[col].transform([input_df[col][0]])

        # Scaling numerikal
        input_df[numerical_cols] = scaler.transform(input_df[numerical_cols])

        # Prediksi
        pred = model.predict(input_df)[0]
        result = le_status.inverse_transform([pred])[0]

        # Tampilkan hasil
        st.write("---")
        if result == "Graduate":
            st.success("🎉 Mahasiswa diprediksi **LULUS**!")
        elif result == "Dropout":
            st.error("⚠️ Mahasiswa diprediksi **DROP OUT**.")
        else:
            st.info(f"Hasil prediksi: {result}")

    except Exception as e:
        st.error("Terjadi kesalahan saat memproses input.")
        st.exception(e)