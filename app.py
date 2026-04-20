import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Simulasi Antrian Ujian",
    page_icon="📋",
    layout="wide"
)

# ============================================================
# HEADER (WAJIB ADA BIAR GA BLANK)
# ============================================================
st.title("📋 Simulasi Antrian Pembagian Lembar Ujian")
st.write("Model: FIFO | Distribusi: Uniform")

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.header("⚙️ Parameter")

n_students = st.sidebar.slider("Jumlah Mahasiswa", 5, 100, 30)
min_dur = st.sidebar.slider("Durasi Minimum", 0.5, 3.0, 1.0)
max_dur = st.sidebar.slider("Durasi Maksimum", 2.0, 8.0, 3.0)
seed = st.sidebar.number_input("Seed", value=2026)

# validasi input
if min_dur >= max_dur:
    st.error("Durasi minimum harus lebih kecil dari maksimum!")
    st.stop()

# ============================================================
# FUNGSI SIMULASI
# ============================================================
def simulate_queue(jml_mhs, dur_min, dur_max, seed=None):
    rng = np.random.default_rng(seed)
    service = rng.uniform(dur_min, dur_max, jml_mhs)

    data = []
    current_time = 0

    for i in range(jml_mhs):
        start = current_time
        finish = start + service[i]

        data.append({
            "Mahasiswa": i+1,
            "Mulai": start,
            "Durasi": service[i],
            "Selesai": finish
        })

        current_time = finish

    df = pd.DataFrame(data)

    return {
        "events": df,
        "service_times": service,
        "total_time": current_time,
        "avg_service": np.mean(service)
    }

# ============================================================
# RUN SIMULASI (SPINNER BIAR KEREN)
# ============================================================
with st.spinner("Menjalankan simulasi..."):
    result = simulate_queue(n_students, min_dur, max_dur, seed)

df = result["events"]

# ============================================================
# METRICS
# ============================================================
c1, c2, c3 = st.columns(3)

c1.metric("Total Waktu", f"{result['total_time']:.2f}")
c2.metric("Rata-rata Durasi", f"{result['avg_service']:.2f}")
c3.metric("Jumlah Mahasiswa", n_students)

# ============================================================
# TABEL DATA (INI YANG BIKIN GA BLANK)
# ============================================================
st.subheader("📊 Data Event")
st.dataframe(df)

# ============================================================
# GANTT CHART
# ============================================================
st.subheader("📅 Gantt Chart")

fig, ax = plt.subplots(figsize=(12,6))

for _, row in df.iterrows():
    ax.barh(row["Mahasiswa"], row["Durasi"], left=row["Mulai"])

ax.set_xlabel("Waktu")
ax.set_ylabel("Mahasiswa")
ax.set_title("Gantt Chart")
ax.invert_yaxis()

st.pyplot(fig)

# ============================================================
# DISTRIBUSI
# ============================================================
st.subheader("📈 Distribusi Durasi")

fig2, ax2 = plt.subplots()
ax2.hist(result["service_times"], bins=20)

st.pyplot(fig2)

# ============================================================
# QQ PLOT (VALIDASI)
# ============================================================
st.subheader("🔍 Q-Q Plot")

fig3 = plt.figure()
stats.probplot(result["service_times"], dist="uniform", plot=plt)
st.pyplot(fig3)

# ============================================================
# DOWNLOAD CSV
# ============================================================
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Data CSV",
    data=csv,
    file_name="simulasi_antrian.csv",
    mime="text/csv"
)

# ============================================================
# DEBUG (ANTI BLANK)
# ============================================================
st.write("✅ Aplikasi berjalan dengan baik")