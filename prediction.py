import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# --- 1. Load Model dan Data ---
model = joblib.load("model.joblib") # Memuat model SVM yang sudah dilatih
df = pd.read_csv("data_cleaned.csv") # Memuat data bersih

# --- 2. Tentukan Fitur-Fitur Penting yang Akan Digunakan ---
# Berdasarkan hasil Permutation Importance yang kamu berikan
# Kamu bisa menyesuaikan jumlah fitur di sini (misal: top 5, top 10, atau top 15)
# Saya akan ambil contoh top 10 untuk keseimbangan
SELECTED_FEATURES = [
    'Curricular_units_2nd_sem_approved',
    'Tuition_fees_up_to_date',
    'Curricular_units_2nd_sem_grade',
    'Curricular_units_1st_sem_approved',
    'Scholarship_holder',
    'Curricular_units_1st_sem_grade',
    'Curricular_units_2nd_sem_evaluations',
    'Application_mode',
    'Unemployment_rate',
    'Course'
]

# --- 3. Siapkan Encoder & Scaler Hanya untuk Fitur yang Dipilih ---
# Pastikan proses encoding dan scaling hanya diterapkan pada SELECTED_FEATURES
X_selected = df[SELECTED_FEATURES].copy() # Buat salinan DataFrame hanya dengan fitur terpilih
y = df["Status"]

# Encoder untuk target 'Status'
le_status = LabelEncoder()
le_status.fit(y)

# Pisahkan fitur kategori dan numerik dari SELECTED_FEATURES
categorical_cols_selected = X_selected.select_dtypes(include='object').columns.tolist()
numerical_cols_selected = X_selected.select_dtypes(include='number').columns.tolist()

# Inisialisasi dan fit encoders untuk fitur kategori yang dipilih
encoders = {}
for col in categorical_cols_selected:
    le = LabelEncoder()
    le.fit(df[col]) # Fit encoder dari data_cleaned asli untuk memastikan semua kategori tercover
    encoders[col] = le

# Inisialisasi dan fit scaler untuk fitur numerik yang dipilih
scaler = MinMaxScaler()
# Lakukan scaling pada data_cleaned asli, tapi hanya untuk kolom numerik terpilih
# Ini penting agar scaler memiliki rentang yang benar berdasarkan data pelatihan
scaler.fit(df[numerical_cols_selected])


# --- 4. Konfigurasi Halaman Streamlit ---
st.set_page_config(page_title="Prediksi Mahasiswa", layout="wide")
st.markdown("<h2 style='text-align:center;'>🎓 Prediksi Status Mahasiswa</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Masukkan data mahasiswa untuk prediksi lulus atau dropout</p>", unsafe_allow_html=True)
st.write("---")

# --- 5. Form Input Prediksi ---
with st.form("form_prediksi"):
    # Kita akan bagi menjadi 2 kolom untuk tampilan yang lebih rapi jika fiturnya sedikit
    cols = st.columns(2)
    input_data = {}

    for idx, col_name in enumerate(SELECTED_FEATURES): # Iterasi hanya pada SELECTED_FEATURES
        col_type = "categorical" if col_name in categorical_cols_selected else "numerical"
        with cols[idx % 2]: # Bagi rata ke 2 kolom
            if col_type == "categorical":
                # Ambil opsi dari df asli untuk kolom tersebut
                options = sorted(df[col_name].dropna().unique())
                input_data[col_name] = st.selectbox(f"{col_name.replace('_', ' ')}", options, key=col_name)
            else:
                # Ambil min/max/median dari df asli untuk kolom tersebut
                min_val = float(df[col_name].min())
                max_val = float(df[col_name].max())
                median_val = float(df[col_name].median())
                input_data[col_name] = st.number_input(f"{col_name.replace('_', ' ')}", min_value=min_val, max_value=max_val, value=median_val, key=col_name)

    submitted = st.form_submit_button("🔍 Prediksi")

# --- 6. Proses Prediksi Saat Form Disubmit ---
if submitted:
    try:
        # Pastikan input_df hanya memiliki kolom-kolom yang dipilih
        input_df = pd.DataFrame([input_data])
        
        # Encode fitur kategori yang dipilih
        for col in categorical_cols_selected:
            input_df[col] = encoders[col].transform(input_df[col])
        
        # Scale fitur numerik yang dipilih
        input_df[numerical_cols_selected] = scaler.transform(input_df[numerical_cols_selected])

        # Prediksi menggunakan model
        pred = model.predict(input_df)[0]
        result = le_status.inverse_transform([pred])[0]

        st.write("---")
        if result == "Graduate":
            st.success("🎉 Mahasiswa diprediksi **LULUS**!")
        else:
            st.error("⚠️ Mahasiswa diprediksi **DROP OUT**.")
    except Exception as e:
        st.error("Terjadi kesalahan saat prediksi. Mohon periksa kembali input Anda.")
        st.exception(e) # Menampilkan detail error untuk debugging