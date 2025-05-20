import streamlit as st
import pandas as pd
import numpy as np
import joblib

from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# Load model
model = joblib.load('model.joblib')

# Load cleaned data untuk referensi kolom dan preprocessing
df = pd.read_csv('data_cleaned.csv')

# ========== PREPROCESSING SETUP ==========
# Encode kategori berdasarkan data latih
cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
cat_cols.remove('Status')  # jangan encode target
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Label Encoder untuk setiap kolom kategori
encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# Scaler untuk kolom numerik
scaler = MinMaxScaler()
df[num_cols] = scaler.fit_transform(df[num_cols])

# ========== STREAMLIT UI ==========
st.title("🎓 Prediksi Status Mahasiswa (Graduate / Dropout)")

st.write("Silakan isi data berikut untuk memprediksi status akhir mahasiswa:")

# Ambil fitur input dari data latih
input_data = {}

for col in df.drop(columns=['Status_enc']).columns:
    if col in cat_cols:
        options = encoders[col].classes_
        value = st.selectbox(f"{col}", options)
        input_data[col] = encoders[col].transform([value])[0]
    elif col in num_cols:
        value = st.number_input(f"{col}", min_value=0.0, step=1.0)
        input_data[col] = value

# Buat DataFrame input
input_df = pd.DataFrame([input_data])

# Normalisasi kolom numerik
input_df[num_cols] = scaler.transform(input_df[num_cols])

# Prediksi
if st.button("Prediksi"):
    pred = model.predict(input_df)[0]
    label = "Graduate" if pred == 1 else "Dropout"
    st.subheader("Hasil Prediksi:")
    st.success(f"✅ Mahasiswa diprediksi akan: **{label}**")