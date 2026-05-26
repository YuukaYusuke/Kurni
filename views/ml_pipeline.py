import pandas as pd
import streamlit as st
from modules.model import MODEL_NAMES
from modules.ui import page_header

def show_ml_pipeline(metrics):
    page_header(
        "Pipeline ML",
        "Dari data mentah sampai model siap dipakai di konsultasi.",
    )

    split = metrics["split"]

    st.markdown('<p class="section-title">1. Pembagian Dataset</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sampel", f"{split['total']:,}")
    c2.metric("Train (64%)", f"{split['train']:,}")
    c3.metric("Validasi (16%)", f"{split['val']:,}")
    c4.metric("Test (20%)", f"{split['test']:,}")

    split_df = pd.DataFrame({
        "Subset": ["Training", "Validasi", "Testing"],
        "Jumlah": [split["train"], split["val"], split["test"]],
        "Persentase": [f"{split['train_pct']}%", f"{split['val_pct']}%", f"{split['test_pct']}%"],
        "Fungsi": [
            "Latih & tuning parameter",
            "Cek performa sementara",
            "Uji final (data belum pernah dilihat model)",
        ],
    })
    st.dataframe(split_df, use_container_width=True, hide_index=True)

    st.markdown(
        f"""
        <div class="info-box">
        <strong>Mode latih:</strong> {metrics.get('training_mode', 'standard')}<br>
        <strong>Dataset mentah:</strong> {metrics.get('raw_samples', 0):,} →
        <strong>Augmentasi range:</strong> {metrics.get('augmented_samples', 0):,} sampel<br>
        <strong>Stratified Split</strong> + <strong>{metrics['cv_folds']}-Fold CV</strong> +
        GridSearch F1-Score<br>
        Fitur numerik: umur, pack-years, batang/hari, lama merokok, + faktor kesehatan.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="section-title">2. Hyperparameter Tuning (GridSearchCV)</p>', unsafe_allow_html=True)

    for key in ["dt", "nb"]:
        m = metrics[key]
        with st.expander(f"{m['name']} — {m['n_combinations']} kombinasi diuji", expanded=(key == "dt")):
            st.markdown("**Parameter terbaik:**")
            st.json(m["best_params"])
            st.metric("Best CV F1-Score (GridSearch)", f"{m['best_cv_f1']:.4f}")

    st.markdown('<p class="section-title">3. Hasil Cross-Validation (5-Fold)</p>', unsafe_allow_html=True)

    cv_data = []
    for key in ["dt", "nb"]:
        m = metrics[key]
        cv_data.append({
            "Model": m["name"],
            "Accuracy (CV)": f"{m['cv_accuracy_mean']:.4f} ± {m['cv_accuracy_std']:.4f}",
            "F1-Score (CV)": f"{m['cv_f1_mean']:.4f} ± {m['cv_f1_std']:.4f}",
            "ROC-AUC (CV)": f"{m['cv_roc_auc_mean']:.4f} ± {m['cv_roc_auc_std']:.4f}",
        })
    st.dataframe(pd.DataFrame(cv_data), use_container_width=True, hide_index=True)

    st.markdown('<p class="section-title">4. Model Terbaik</p>', unsafe_allow_html=True)
    best = metrics[metrics["best_model_key"]]
    st.success(
        f"**{metrics['best_model']}** — F1 test **{best['f1']:.4f}**, "
        f"ROC-AUC **{best['roc_auc']:.4f}**"
    )

    st.markdown('<p class="section-title">Alur Kerja ML</p>', unsafe_allow_html=True)
    st.markdown(
        """
        ```
        Dataset (30.000+) 
            → Konversi ke Fitur Numerik (Range) 
            → Augmentasi Sampel dalam Range 
            → Split Train / Val / Test 
            → GridSearchCV + 5-Fold CV 
            → Model + Tolok Ukur Dataset 
            → Prediksi Konsultasi (input manual range)
        ```
        """
    )
