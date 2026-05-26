import streamlit as st
from modules.features import augment_range_samples, build_benchmarks, build_training_data
from modules.load_data import load_dataset
from modules.model import train_models
from modules.preprocess import preprocess_data
from modules.ui import MENU_OPTIONS, inject_custom_css, render_sidebar_brand, render_sidebar_health_badge
from views.beranda import show_beranda
from views.evaluasi_model import show_evaluasi
from views.history import show_history
from views.ml_pipeline import show_ml_pipeline
from views.prediksi import show_prediksi
from views.preprocessing import show_preprocessing

st.set_page_config(
    page_title="ParuSehat | Sistem Cerdas ML",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

if "history" not in st.session_state:
    st.session_state.history = []


@st.cache_resource(show_spinner="Melatih model ML (range numeric + augmentasi + GridSearch)...")
def prepare_models():
    df = load_dataset("data/dataset.csv")
    df_processed, encoders = preprocess_data(df)

    X_num, y_num = build_training_data(df)
    X_train_aug, y_train_aug = augment_range_samples(X_num, y_num, multiplier=3)
    benchmarks = build_benchmarks(X_num, y_num)

    dt_model, nb_model, metrics, feature_names, models = train_models(X_train_aug, y_train_aug)
    metrics["training_mode"] = "range_numeric_augmented"
    metrics["benchmarks"] = benchmarks
    metrics["raw_samples"] = len(X_num)
    metrics["augmented_samples"] = len(X_train_aug)

    return df, df_processed, encoders, models, metrics, feature_names, benchmarks


df, df_processed, encoders, models, metrics, feature_names, benchmarks = prepare_models()

render_sidebar_brand()
render_sidebar_health_badge()

menu = st.sidebar.radio("Navigasi", MENU_OPTIONS, label_visibility="collapsed")

st.sidebar.divider()
st.sidebar.markdown("##### Status Model")
st.sidebar.success(f"Best: {metrics['best_model']}")
st.sidebar.caption(f"F1 = {metrics[metrics['best_model_key']]['f1']:.4f}")
st.sidebar.divider()
st.sidebar.caption("ParuSehat · screening paru interaktif")
st.sidebar.caption("sponsored by PT Marbol")

if menu == "Beranda":
    show_beranda(df, metrics)
elif menu == "Dataset & Preprocessing":
    show_preprocessing(df, df_processed, encoders)
elif menu == "Pipeline ML":
    show_ml_pipeline(metrics)
elif menu == "Konsultasi":
    show_prediksi(models, df, encoders, metrics, benchmarks)
elif menu == "Evaluasi Model":
    show_evaluasi(models, feature_names, metrics)
elif menu == "Riwayat":
    show_history()
