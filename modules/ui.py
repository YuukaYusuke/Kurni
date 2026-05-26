import streamlit as st

COLUMN_LABELS = {
    "Usia": "Kelompok Usia",
    "Jenis_Kelamin": "Jenis Kelamin",
    "Merokok": "Status Merokok",
    "Bekerja": "Status Bekerja",
    "Rumah_Tangga": "Rumah Tangga",
    "Aktivitas_Begadang": "Aktivitas Begadang",
    "Aktivitas_Olahraga": "Frekuensi Olahraga",
    "Asuransi": "Kepemilikan Asuransi",
    "Penyakit_Bawaan": "Penyakit Bawaan",
    "Hasil": "Risiko Penyakit Paru-Paru",
}

FEATURE_HELP = {
    "Usia": "Kelompok usia dipakai model sebagai referensi — bukan pengganti angka umur di form.",
    "Jenis_Kelamin": "Variabel demografis dari dataset.",
    "Merokok": "Status aktif/pasif; slider batang & tahun tetap dipakai untuk skor klinis.",
    "Bekerja": "Pekerjaan bisa terkait paparan debu/polusi di dataset.",
    "Rumah_Tangga": "Pola hidup rumah tangga dalam data latih.",
    "Aktivitas_Begadang": "Begadang sering ikut pola hidup yang mempengaruhi recovery paru.",
    "Aktivitas_Olahraga": "Olahraga rutin biasanya mendukung kapasitas paru.",
    "Asuransi": "Akses layanan kesehatan — variabel di dataset, bukan diagnosis.",
    "Penyakit_Bawaan": "Riwayat penyakit lain yang bisa naikkan risiko komplikasi paru.",
}

MODEL_INFO = {
    "Decision Tree": {
        "icon": "🌳",
        "desc": (
            "**Decision Tree** — pohon keputusan yang gampang dibaca. "
            "Hyperparameter disetel otomatis lewat GridSearch."
        ),
        "key": "dt",
    },
    "Naive Bayes": {
        "icon": "📊",
        "desc": (
            "**Naive Bayes** — cepat, cocok untuk fitur ter-encoding. "
            "`var_smoothing` ikut dituning."
        ),
        "key": "nb",
    },
}

MENU_OPTIONS = [
    "Beranda",
    "Dataset & Preprocessing",
    "Pipeline ML",
    "Konsultasi",
    "Evaluasi Model",
    "Riwayat",
]

def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f766e 0%, #134e4a 100%);
        }

        [data-testid="stSidebar"] *:not(.sidebar-health-badge):not(.sidebar-health-badge *) {
            color: #ecfdf5 !important;
        }

        .sidebar-health-badge, .sidebar-health-badge * {
            color: inherit !important;
        }

        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stSelectbox label {
            color: #d1fae5 !important;
            font-weight: 500;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.15);
        }

        .hero-card {
            background: linear-gradient(135deg, #0d9488 0%, #0f766e 55%, #115e59 100%);
            border-radius: 20px;
            padding: 2.5rem 2rem;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 20px 40px rgba(15, 118, 110, 0.25);
        }

        .hero-card h1 {
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 0.75rem 0;
            color: white !important;
        }

        .hero-card p {
            font-size: 1.05rem;
            opacity: 0.92;
            margin: 0;
            line-height: 1.6;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.25rem 1rem;
            text-align: center;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
            height: 100%;
        }

        .metric-card .value {
            font-size: 1.75rem;
            font-weight: 700;
            color: #0f766e;
            margin: 0.25rem 0;
        }

        .metric-card .label {
            font-size: 0.85rem;
            color: #64748b;
            font-weight: 500;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #0f172a;
            margin: 1.5rem 0 0.75rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #99f6e4;
            display: inline-block;
        }

        .info-box {
            background: #f0fdfa;
            border-left: 4px solid #14b8a6;
            border-radius: 0 12px 12px 0;
            padding: 1rem 1.25rem;
            margin: 1rem 0;
            color: #134e4a;
        }

        .result-positive {
            background: linear-gradient(135deg, #fef2f2, #fff1f2);
            border: 1px solid #fecaca;
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
        }

        .result-negative {
            background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
            border: 1px solid #bbf7d0;
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0d9488, #0f766e);
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.6rem 1.5rem;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #0f766e, #115e59);
            border: none;
        }

        div[data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 0.75rem 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle=""):
    st.markdown(
        f"""
        <div class="hero-card">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def label_column(col):
    return COLUMN_LABELS.get(col, col.replace("_", " "))

def render_sidebar_brand():
    st.sidebar.markdown(
        """
        <div style="text-align:center;padding:0.5rem 0 1.5rem 0;">
            <div style="font-size:2.5rem;line-height:1;">🫁</div>
            <div style="font-size:1.1rem;font-weight:700;margin-top:0.5rem;">
                ParuSehat
            </div>
            <div style="font-size:0.8rem;opacity:0.85;margin-top:0.25rem;">
                Cek paru, napas lebih tenang
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.divider()


def render_sidebar_health_badge():
    from modules.smoking_tiers import render_sidebar_health_badge as _badge
    _badge()
