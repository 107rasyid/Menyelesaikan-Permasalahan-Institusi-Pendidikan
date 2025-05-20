import streamlit as st
import pandas as pd
import numpy as np
import joblib

from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# === Load model ===
model = joblib.load('model.joblib')

# === Load cleaned data (tanpa Status_enc) untuk info kolom ===
df = pd.read_csv('data_cleaned.csv')

# === Buat encoder untuk input (pakai data asli supaya encoding konsisten) ===
X = df.drop(columns=['Status'])
y = df['Status']

# Simpan label encoder dari training
le_status = LabelEncoder()
le_status.fit(y)

# Encode categorical features
X_encoded = X.copy()
for col in X_encoded.select_dtypes(include='object').columns:
    X_encoded[col] = LabelEncoder().fit_transform(X_encoded[col])

# Scale numerical
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X_encoded)

# Simpan informasi kolom
categorical_cols = X.select_dtypes(include='object').columns.tolist()
numerical_cols = X.select_dtypes(include=np.number).columns.tolist()
input_cols = categorical_cols + numerical_cols

# === Streamlit UI ===
st.title("🎓 Prediksi Status Mahasiswa (Graduate / Dropout)")
st.write("Silakan isi data berikut untuk memprediksi status akhir mahasiswa:")

# Form untuk input satu per satu
user_input = {}
with st.form("input_form"):
    for col in categorical_cols:
        options = sorted(df[col].dropna().unique().tolist())
        user_input[col] = st.selectbox(col, options)

    for col in numerical_cols:
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        user_input[col] = st.slider(col, min_val, max_val, float(df[col].median()))

    submitted = st.form_submit_button("Prediksi")

if submitted:
    try:
        # Masukkan input ke DataFrame
        input_df = pd.DataFrame([user_input])

        # Encode categorical
        for col in categorical_cols:
            le = LabelEncoder()
            le.fit(df[col])
            input_df[col] = le.transform(input_df[col])

        # Scale numerical
        input_df[numerical_cols] = scaler.transform(input_df[numerical_cols])

        # Prediksi
        prediction = model.predict(input_df)[0]
        pred_label = le_status.inverse_transform([prediction])[0]

        st.success(f"✅ Prediksi Status Mahasiswa: **{pred_label}**")

    except Exception as e:
        st.error("Terjadi kesalahan saat memproses input.")
        st.exception(e)