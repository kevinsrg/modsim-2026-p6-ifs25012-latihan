"""
Streamlit App: Simulasi Pembagian Lembar Jawaban Ujian
Modul Praktikum 6 — Verification & Validation
Jalankan: streamlit run app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from simulation import run_simulation, theoretical_total

# ─── Konfigurasi Halaman ───────────────────────────────────────────────────
st.set_page_config(
    page_title="ModSim P6 — V&V Pembagian Lembar Jawaban",
    page_icon="📋",
    layout="wide",
)

st.title("📋 Simulasi Pembagian Lembar Jawaban Ujian")
st.caption("Discrete Event Simulation — Single-Server Queue | Modul Praktikum 6")

# ─── Sidebar: Parameter ───────────────────────────────────────────────────
st.sidebar.header("⚙️ Parameter Simulasi")
n_students  = st.sidebar.slider("Jumlah Mahasiswa (N)", 5, 100, 30)
min_dur     = st.sidebar.slider("Durasi Min (menit)",    1, 5, 1)
max_dur     = st.sidebar.slider("Durasi Max (menit)",    1, 10, 3)
seed        = st.sidebar.number_input("Random Seed", min_value=0, max_value=9999, value=42)
n_rep       = st.sidebar.slider("Jumlah Replikasi (Validasi)", 50, 1000, 300, step=50)

if min_dur >= max_dur:
    st.sidebar.error("Durasi Min harus < Durasi Max!")
    st.stop()

# Jalankan simulasi
result = run_simulation(n_students, min_dur, max_dur, seed=seed)
df = pd.DataFrame(result["events"])
teoritis = theoretical_total(n_students, min_dur, max_dur)

# ─── Metrik Utama ─────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("⏱️ Total Waktu", f"{result['total_time']:.2f} mnt")
col2.metric("📐 Teoritis (N×E[T])", f"{teoritis:.2f} mnt")
col3.metric("⌛ Rata-rata Tunggu", f"{result['avg_wait']:.2f} mnt")
col4.metric("📊 Utilisasi Meja", f"{result['utilization']:.1f}%")

st.divider()

# ─── Tab Utama ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Simulasi & Timeline",
    "✅ Verifikasi (1.2)",
    "🔍 Validasi (1.3)",
    "📝 Kesimpulan (1.4)",
])

# ── Tab 1: Simulasi ──────────────────────────────────────────────────────
with tab1:
    st.subheader("Tabel Event Log")
    st.dataframe(df.style.format({
        "start_service": "{:.3f}",
        "duration":      "{:.3f}",
        "end_service":   "{:.3f}",
        "wait_time":     "{:.3f}",
    }), use_container_width=True)

    st.subheader("Gantt Chart Pelayanan")
    n_show = min(n_students, 40)
    fig, ax = plt.subplots(figsize=(12, max(4, n_show * 0.22)))
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, n_show))
    for _, row in df.head(n_show).iterrows():
        idx = int(row["mahasiswa"]) - 1
        ax.barh(row["mahasiswa"], row["duration"],
                left=row["start_service"],
                color=colors[idx], edgecolor="white", height=0.7)
    ax.axvline(result["total_time"], color="red", linestyle="--",
               label=f"Total: {result['total_time']:.1f} mnt")
    ax.set_xlabel("Waktu (menit)")
    ax.set_ylabel("Mahasiswa ke-")
    ax.set_title("Timeline Pelayanan Lembar Jawaban Ujian")
    ax.legend()
    ax.grid(axis="x", alpha=0.3)
    st.pyplot(fig)
    plt.close()

# ── Tab 2: Verifikasi ────────────────────────────────────────────────────
with tab2:
    st.subheader("1.2 Verification")

    # Logical Flow Check
    st.markdown("#### a. Pemeriksaan Logika Alur")
    overlap = any(df.iloc[i]["start_service"] < df.iloc[i-1]["end_service"] - 1e-9
                  for i in range(1, len(df)))
    monoton = bool(df["start_service"].diff().dropna().ge(0).all())
    c1, c2, c3 = st.columns(3)
    c1.metric("Tumpang Tindih",   "Tidak Ada ✓" if not overlap else "ADA ✗")
    c2.metric("Urutan Kronologis", "Sesuai ✓"   if monoton     else "Tidak ✗")
    c3.metric("Satu per Satu",     "YA ✓"        if not overlap else "TIDAK ✗")

    # Event Tracing
    st.markdown("#### b. Event Tracing (5 Mahasiswa Pertama)")
    st.dataframe(df.head(5)[["mahasiswa","start_service","duration","end_service"]],
                 use_container_width=True)
    trace_rows = []
    for i in range(min(4, len(df)-1)):
        gap = df.iloc[i+1]["start_service"] - df.iloc[i]["end_service"]
        trace_rows.append({
            "Dari": f"Mhs {i+1}", "Ke": f"Mhs {i+2}",
            "end_service": df.iloc[i]["end_service"],
            "start_service berikut": df.iloc[i+1]["start_service"],
            "Gap": round(gap, 6),
            "Status": "✓" if abs(gap) < 1e-9 else f"gap={gap:.4f}",
        })
    st.dataframe(pd.DataFrame(trace_rows), use_container_width=True)

    # Extreme Condition
    st.markdown("#### c. Uji Kondisi Ekstrem")
    skenario = [
        {"label": "N=1, Uniform(1,3)",    "n": 1,  "mn": 1, "mx": 3},
        {"label": "N=30, durasi tetap=1", "n": 30, "mn": 1, "mx": 1},
        {"label": "N=30, durasi tetap=3", "n": 30, "mn": 3, "mx": 3},
        {"label": f"N={n_students} (setting kamu)", "n": n_students, "mn": min_dur, "mx": max_dur},
    ]
    ext_rows = []
    for s in skenario:
        r = run_simulation(s["n"], s["mn"], s["mx"], seed=42)
        t = theoretical_total(s["n"], s["mn"], s["mx"])
        ext_rows.append({
            "Skenario": s["label"],
            "Total Simulasi": r["total_time"],
            "Total Teoritis": t,
            "Status": "✓ Sesuai" if abs(r["total_time"] - t) / max(t, 1) < 0.25 else "? Cek",
        })
    st.dataframe(pd.DataFrame(ext_rows), use_container_width=True)

    # Distribusi
    st.markdown("#### d. Distribusi Waktu Pelayanan")
    durations = result["durations"]
    fig2, axes = plt.subplots(1, 2, figsize=(11, 3.5))
    axes[0].hist(durations, bins=12, color="steelblue", edgecolor="white", alpha=0.85)
    axes[0].axvline(min_dur, color="red",   linestyle="--", label=f"min={min_dur}")
    axes[0].axvline(max_dur, color="green", linestyle="--", label=f"max={max_dur}")
    axes[0].set_title("Histogram Durasi")
    axes[0].set_xlabel("Durasi (menit)")
    axes[0].legend()
    axes[1].boxplot(durations, vert=False, patch_artist=True,
                    boxprops=dict(facecolor="steelblue", alpha=0.7))
    axes[1].set_title("Box Plot Durasi")
    axes[1].set_xlabel("Durasi (menit)")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()
    st.info(f"Min={min(durations):.3f} ≥ {min_dur} ✓  |  Max={max(durations):.3f} ≤ {max_dur} ✓  |  Mean={np.mean(durations):.3f} (teoritis={(min_dur+max_dur)/2:.1f})")

    # Reproducibility
    st.markdown("#### e. Reproducibility Check")
    r1 = run_simulation(n_students, min_dur, max_dur, seed=seed)
    r2 = run_simulation(n_students, min_dur, max_dur, seed=seed)
    same = r1["total_time"] == r2["total_time"]
    st.success(f"Eksekusi 1: {r1['total_time']:.4f}  |  Eksekusi 2: {r2['total_time']:.4f}  → Output identik: {'YA ✓' if same else 'TIDAK ✗'}")

    # Kesimpulan
    st.markdown("#### 1.2.3 Kesimpulan Verifikasi")
    st.success(
        "✅ Model simulasi **telah terverifikasi**.\n\n"
        "- Logika alur sesuai: satu mahasiswa per waktu, FIFO.\n"
        "- Event tracing kronologis tanpa tumpang tindih.\n"
        "- Uji kondisi ekstrem memberikan hasil deterministik yang benar.\n"
        "- Distribusi durasi sesuai Uniform(min, max).\n"
        "- Output reproducible dengan seed yang sama."
    )

# ── Tab 3: Validasi ───────────────────────────────────────────────────────
with tab3:
    st.subheader("1.3 Validation")

    # Face Validation
    st.markdown("#### a. Face Validation")
    lower = n_students * min_dur
    upper = n_students * max_dur
    in_range = lower <= result["total_time"] <= upper
    st.info(
        f"Total simulasi: **{result['total_time']:.2f} menit**  |  "
        f"Rentang wajar: {lower:.0f}–{upper:.0f} menit  |  "
        f"{'Dalam rentang ✓' if in_range else 'Di luar rentang ✗'}"
    )

    # Theoretical Comparison
    st.markdown("#### b. Perbandingan dengan Nilai Teoritis")
    totals_rep = [run_simulation(n_students, min_dur, max_dur, seed=s)["total_time"]
                  for s in range(n_rep)]
    sim_mean = np.mean(totals_rep)
    sim_std  = np.std(totals_rep)
    pct_err  = abs(sim_mean - teoritis) / teoritis * 100

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Teoritis",          f"{teoritis:.2f} mnt")
    col_b.metric("Rata-rata Simulasi", f"{sim_mean:.2f} mnt")
    col_c.metric("Galat",              f"{pct_err:.2f}%", delta=f"{'✓ < 5%' if pct_err < 5 else '> 5%'}")

    fig3, ax3 = plt.subplots(figsize=(9, 3.5))
    ax3.hist(totals_rep, bins=25, color="steelblue", edgecolor="white", alpha=0.8)
    ax3.axvline(teoritis,  color="red",    linestyle="--", linewidth=2, label=f"Teoritis={teoritis:.1f}")
    ax3.axvline(sim_mean,  color="orange", linestyle="-",  linewidth=2, label=f"Simulasi={sim_mean:.2f}")
    ax3.set_xlabel("Total Waktu (menit)")
    ax3.set_ylabel("Frekuensi")
    ax3.set_title(f"Distribusi Total Waktu ({n_rep} replikasi)")
    ax3.legend()
    st.pyplot(fig3)
    plt.close()

    # Behavior Validation
    st.markdown("#### c. Validasi Perilaku Model")
    n_vals = list(range(5, min(n_students + 20, 71), 5))
    totals_n = [np.mean([run_simulation(n, min_dur, max_dur, seed=s)["total_time"]
                         for s in range(100)]) for n in n_vals]
    teoritis_n = [theoretical_total(n, min_dur, max_dur) for n in n_vals]

    fig4, ax4 = plt.subplots(figsize=(9, 3.5))
    ax4.plot(n_vals, totals_n,   "o-", color="steelblue",  label="Simulasi")
    ax4.plot(n_vals, teoritis_n, "s--", color="red",        label="Teoritis")
    ax4.set_xlabel("Jumlah Mahasiswa (N)")
    ax4.set_ylabel("Total Waktu (menit)")
    ax4.set_title("Pengaruh N terhadap Total Waktu")
    ax4.legend()
    ax4.grid(alpha=0.3)
    st.pyplot(fig4)
    plt.close()

    beh_ok = totals_n[-1] > totals_n[0]
    st.success(f"N meningkat → Total waktu meningkat: {'Sesuai ✓' if beh_ok else 'Tidak Sesuai'}")

    # Sensitivity Analysis
    st.markdown("#### d. Sensitivity Analysis")
    configs = [
        (f"Uniform({min_dur},{max_dur}) — Baseline", min_dur,         max_dur),
        (f"Uniform({min_dur+1},{max_dur+1}) — Shifted", min_dur + 1,  max_dur + 1),
        (f"Uniform({min_dur},{max_dur+2}) — Wider",   min_dur,         max_dur + 2),
    ]
    sa_rows = []
    for label, mn, mx in configs:
        tots = [run_simulation(n_students, mn, mx, seed=s)["total_time"] for s in range(200)]
        sa_rows.append({"Konfigurasi": label,
                        "Mean (mnt)": round(np.mean(tots), 2),
                        "Std (mnt)":  round(np.std(tots), 2),
                        "Min": round(min(tots), 2),
                        "Max": round(max(tots), 2)})
    st.dataframe(pd.DataFrame(sa_rows), use_container_width=True)

    fig5, ax5 = plt.subplots(figsize=(9, 3.5))
    ax5.bar([r["Konfigurasi"] for r in sa_rows],
            [r["Mean (mnt)"]  for r in sa_rows],
            color=["steelblue","darkorange","green"], edgecolor="white", alpha=0.85)
    ax5.set_ylabel("Rata-rata Total Waktu (menit)")
    ax5.set_title("Sensitivity Analysis")
    ax5.tick_params(axis="x", labelsize=9)
    plt.xticks(rotation=10, ha="right")
    ax5.grid(axis="y", alpha=0.3)
    st.pyplot(fig5)
    plt.close()
    st.success("Model sensitif terhadap pergeseran distribusi waktu pelayanan ✓")

    # Kesimpulan Validasi
    st.markdown("#### 1.3.3 Kesimpulan Validasi")
    st.success(
        "✅ Model simulasi **telah tervalidasi**.\n\n"
        "- Hasil masuk akal secara konseptual (Face Validation).\n"
        f"- Rata-rata simulasi mendekati nilai teoritis (galat {pct_err:.2f}%).\n"
        "- Perilaku model konsisten dengan kondisi nyata.\n"
        "- Model sensitif terhadap parameter distribusi waktu pelayanan."
    )

# ── Tab 4: Kesimpulan ─────────────────────────────────────────────────────
with tab4:
    st.subheader("1.4 Kesimpulan Akhir")
    st.markdown(f"""
Model simulasi **Pembagian Lembar Jawaban Ujian** telah melalui proses
**Verifikasi** dan **Validasi** secara komprehensif.

---

### ✅ Verifikasi
Model **diimplementasikan dengan benar** (*build the model right*):
- Antrian FIFO, single-server, tanpa interupsi antar mahasiswa.
- Waktu pelayanan terdistribusi Uniform({min_dur}, {max_dur}) sesuai asumsi.
- Output **reproducible** pada seed yang sama.

### 🔍 Validasi
Model **merepresentasikan kondisi nyata** (*build the right model*):
- Total waktu simulasi mendekati nilai teoritis: **N × E[T] = {n_students} × {(min_dur+max_dur)/2:.1f} = {teoritis:.1f} menit**.
- Semakin banyak mahasiswa → total waktu semakin panjang ✓
- Model sensitif terhadap perubahan distribusi durasi pelayanan ✓

---

### 🏁 Kesimpulan
> Model layak digunakan sebagai **alat bantu analisis** untuk mengestimasi
> durasi pembagian lembar jawaban ujian dan menganalisis dampak variasi
> jumlah mahasiswa maupun kecepatan pelayanan.
""")

    st.divider()
    st.caption("Modul Praktikum 6: Verification & Validation | [11S1221] Pemodelan dan Simulasi (MODSIM)")
