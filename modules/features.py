"""Fitur numerik berbasis range — dataset jadi tolok ukur, input manual langsung ke model."""

import numpy as np
import pandas as pd

FEATURE_COLS = [
    "umur",
    "pack_years",
    "batang_hari",
    "lama_merokok",
    "jenis_kelamin",
    "merokok_aktif",
    "bekerja",
    "rumah_tangga",
    "begadang",
    "olahraga_jarang",
    "asuransi",
    "penyakit_bawaan",
]

RANGES = {
    "umur": (17, 80),
    "pack_years": (0, 40),
    "batang_hari": (0, 30),
    "lama_merokok": (0, 50),
}

BOOL_MAP = {
    "Ya": 1,
    "Tidak": 0,
    "Ada": 1,
    "Pria": 1,
    "Wanita": 0,
    "Aktif": 1,
    "Pasif": 0,
    "Sering": 0,
    "Jarang": 1,
}


def _estimate_smoking_from_category(merokok: str) -> tuple[float, float, float]:
    """Estimasi numerik dari kategori dataset (untuk training)."""
    if merokok == "Aktif":
        return 8.0, 5.0, 8.0
    return 0.0, 0.0, 12.0


def dataset_row_to_numeric(row) -> dict:
    umur = 32 if row["Usia"] == "Muda" else 55
    batang, lama, pack = _estimate_smoking_from_category(row["Merokok"])
    if pack == 0 and lama > 0:
        pack = (batang * lama) / 20.0

    return {
        "umur": float(umur),
        "pack_years": float(pack),
        "batang_hari": float(batang),
        "lama_merokok": float(lama),
        "jenis_kelamin": float(BOOL_MAP[row["Jenis_Kelamin"]]),
        "merokok_aktif": float(BOOL_MAP[row["Merokok"]]),
        "bekerja": float(BOOL_MAP[row["Bekerja"]]),
        "rumah_tangga": float(BOOL_MAP[row["Rumah_Tangga"]]),
        "begadang": float(BOOL_MAP[row["Aktivitas_Begadang"]]),
        "olahraga_jarang": float(BOOL_MAP[row["Aktivitas_Olahraga"]]),
        "asuransi": float(BOOL_MAP[row["Asuransi"]]),
        "penyakit_bawaan": float(BOOL_MAP[row["Penyakit_Bawaan"]]),
    }


def profile_to_numeric(profile: dict, user_input: dict) -> dict:
    """Input manual user → vektor numerik (boleh di luar kombinasi dataset)."""
    batang = float(profile.get("batang_per_hari", 0) or 0)
    lama = float(profile.get("lama_merokok", 0) or 0)
    pack = round((batang * lama) / 20.0, 2)

    return {
        "umur": float(profile.get("umur", 25)),
        "pack_years": pack,
        "batang_hari": batang,
        "lama_merokok": lama,
        "jenis_kelamin": float(BOOL_MAP.get(user_input.get("Jenis_Kelamin", "Pria"), 1)),
        "merokok_aktif": float(BOOL_MAP.get(user_input.get("Merokok", "Pasif"), 0)),
        "bekerja": float(BOOL_MAP.get(user_input.get("Bekerja", "Tidak"), 0)),
        "rumah_tangga": float(BOOL_MAP.get(user_input.get("Rumah_Tangga", "Tidak"), 0)),
        "begadang": float(BOOL_MAP.get(user_input.get("Aktivitas_Begadang", "Tidak"), 0)),
        "olahraga_jarang": float(BOOL_MAP.get(user_input.get("Aktivitas_Olahraga", "Sering"), 0)),
        "asuransi": float(BOOL_MAP.get(user_input.get("Asuransi", "Tidak"), 0)),
        "penyakit_bawaan": float(BOOL_MAP.get(user_input.get("Penyakit_Bawaan", "Tidak"), 0)),
    }


def build_training_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    rows = [dataset_row_to_numeric(row) for _, row in df.iterrows()]
    X = pd.DataFrame(rows, columns=FEATURE_COLS)
    y = (df["Hasil"] == "Ya").astype(int)
    return X, y


def augment_range_samples(X: pd.DataFrame, y: pd.Series, multiplier: int = 3) -> tuple[pd.DataFrame, pd.Series]:
    """
    Tambah sampel sintetis di dalam range agar model belajar pola kontinu,
    bukan hanya kombinasi kategori yang ada di dataset.
    """
    rng = np.random.default_rng(42)
    parts_X = [X]
    parts_y = [y]

    for _ in range(multiplier):
        noise = X.copy()
        noise["umur"] = (noise["umur"] + rng.integers(-8, 9, len(noise))).clip(*RANGES["umur"])
        noise["batang_hari"] = (noise["batang_hari"] + rng.integers(-2, 3, len(noise))).clip(
            *RANGES["batang_hari"]
        )
        noise["lama_merokok"] = (noise["lama_merokok"] + rng.integers(-3, 4, len(noise))).clip(
            *RANGES["lama_merokok"]
        )
        noise["pack_years"] = (noise["batang_hari"] * noise["lama_merokok"] / 20.0).round(2)
        parts_X.append(noise)
        parts_y.append(y)

    X_aug = pd.concat(parts_X, ignore_index=True)
    y_aug = pd.concat(parts_y, ignore_index=True)
    return X_aug, y_aug


def build_benchmarks(X: pd.DataFrame, y: pd.Series) -> dict:
    """Statistik dataset sebagai tolok ukur (range, mean, persentil)."""
    benchmarks = {}
    for col in FEATURE_COLS:
        s = X[col]
        benchmarks[col] = {
            "min": float(s.min()),
            "max": float(s.max()),
            "mean": float(s.mean()),
            "p25": float(s.quantile(0.25)),
            "p50": float(s.quantile(0.50)),
            "p75": float(s.quantile(0.75)),
        }

    risk_rate = y.mean()
    benchmarks["_meta"] = {
        "total_samples": int(len(X)),
        "risk_positive_rate": float(risk_rate),
        "mode": "range_numeric",
    }
    return benchmarks


def compare_to_benchmark(values: dict, benchmarks: dict) -> list[dict]:
    """Bandingkan input user vs tolok ukur dataset."""
    notes = []
    for col in ["umur", "pack_years", "batang_hari", "lama_merokok"]:
        if col not in values or col not in benchmarks:
            continue
        v = values[col]
        b = benchmarks[col]
        if v > b["p75"]:
            level = "lebih tinggi dari kebanyakan di dataset"
        elif v < b["p25"]:
            level = "lebih rendah dari kebanyakan di dataset"
        else:
            level = "masih di rentang umum dataset"
        notes.append({
            "fitur": col,
            "nilai": v,
            "range_dataset": f"{b['min']:.1f} – {b['max']:.1f}",
            "rata_rata": f"{b['mean']:.1f}",
            "level": level,
        })
    return notes


def numeric_to_dataframe(values: dict) -> pd.DataFrame:
    return pd.DataFrame([[values[c] for c in FEATURE_COLS]], columns=FEATURE_COLS)
