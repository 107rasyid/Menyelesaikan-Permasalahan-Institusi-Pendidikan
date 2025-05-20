import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# Load model dan data
model = joblib.load("model.joblib")
df = pd.read_csv("data_cleaned.csv")

# Setup encoder & scaler
X = df.drop(columns=["Status"])
y = df["Status"]

le_status = LabelEncoder()
le_status.fit(y)

categorical_cols = X.select_dtypes(include='object').columns.tolist()
numerical_cols = X.select_dtypes(include='number').columns.tolist()

encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    le.fit(df[col])
    encoders[col] = le

scaler = MinMaxScaler()
scaled_X = X.copy()
for col in categorical_cols:
    scaled_X[col] = encoders[col].transform(X[col])
scaler.fit(scaled_X[numerical_cols])

st.set_page_config(page_title="Prediksi Mahasiswa", layout="wide")
st.markdown("<h2 style='text-align:center;'>🎓 Prediksi Status Mahasiswa</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Masukkan data mahasiswa untuk prediksi lulus atau dropout</p>", unsafe_allow_html=True)
st.write("---")

with st.form("form_prediksi"):
    cols = st.columns(3)  # 3 kolom
    input_data = {}

    # Gabungkan semua kolom (kategori + numerik) biar bisa dibagi merata
    all_cols = categorical_cols + numerical_cols

    for idx, col in enumerate(all_cols):
        col_type = "categorical" if col in categorical_cols else "numerical"
        with cols[idx % 3]:
            if col_type == "categorical":
                options = sorted(df[col].dropna().unique())
                input_data[col] = st.selectbox(f"{col}", options, key=col)
            else:
                min_val = float(df[col].min())
                max_val = float(df[col].max())
                median_val = float(df[col].median())
                input_data[col] = st.number_input(f"{col}", min_value=min_val, max_value=max_val, value=median_val, key=col)

    submitted = st.form_submit_button("🔍 Prediksi")

if submitted:
    try:
        input_df = pd.DataFrame([input_data])
        for col in categorical_cols:
            input_df[col] = encoders[col].transform(input_df[col])
        input_df[numerical_cols] = scaler.transform(input_df[numerical_cols])

        pred = model.predict(input_df)[0]
        result = le_status.inverse_transform([pred])[0]

        st.write("---")
        if result == "Graduate":
            st.success("🎉 Mahasiswa diprediksi **LULUS**!")
        else:
            st.error("⚠️ Mahasiswa diprediksi **DROP OUT**.")
    except Exception as e:
        st.error("Terjadi kesalahan saat prediksi.")
        st.exception(e)
