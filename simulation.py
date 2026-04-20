"""
Simulasi Pembagian Lembar Jawaban Ujian
Discrete Event Simulation - Single Server Queue
Modul Praktikum 6: Verification & Validation
"""

import random
import numpy as np
import pandas as pd


def run_simulation(n_students: int = 30,
                   min_duration: float = 1.0,
                   max_duration: float = 3.0,
                   seed: int = None) -> dict:
    """
    Jalankan simulasi pembagian lembar jawaban ujian.

    Parameters
    ----------
    n_students   : jumlah mahasiswa
    min_duration : durasi minimum pelayanan (menit) - distribusi Uniform
    max_duration : durasi maksimum pelayanan (menit) - distribusi Uniform
    seed         : random seed (None = acak)

    Returns
    -------
    dict berisi:
        - events      : list of dict (event log per mahasiswa)
        - total_time  : total waktu pembagian (menit)
        - avg_wait    : rata-rata waktu tunggu (menit)
        - utilization : utilisasi meja pengajar (%)
        - durations   : list durasi pelayanan tiap mahasiswa
    """
    rng = random.Random(seed)

    events = []
    current_time = 0.0

    for i in range(1, n_students + 1):
        start_service = current_time          # langsung dilayani (FIFO, 1 server)
        duration = rng.uniform(min_duration, max_duration)
        end_service = start_service + duration
        wait_time = start_service - (events[-1]["end_service"] if i > 1 else 0)
        # Untuk mahasiswa pertama, waktu tunggu = 0

        events.append({
            "mahasiswa": i,
            "start_service": round(start_service, 4),
            "duration": round(duration, 4),
            "end_service": round(end_service, 4),
            "wait_time": round(max(0.0, wait_time), 4),
        })
        current_time = end_service

    total_time = events[-1]["end_service"]
    avg_wait = np.mean([e["wait_time"] for e in events])
    # Utilisasi: server selalu sibuk dalam sistem single-server FIFO tanpa arrival gap
    utilization = (total_time / total_time) * 100 if total_time > 0 else 0

    return {
        "events": events,
        "total_time": round(total_time, 4),
        "avg_wait": round(avg_wait, 4),
        "utilization": round(utilization, 2),
        "durations": [e["duration"] for e in events],
    }


def theoretical_total(n_students: int,
                      min_duration: float = 1.0,
                      max_duration: float = 3.0) -> float:
    """Total waktu teoritis = N × E[Uniform(min,max)]"""
    expected = (min_duration + max_duration) / 2
    return n_students * expected
