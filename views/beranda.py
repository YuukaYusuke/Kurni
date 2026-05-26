import streamlit as st
from modules.ui import metric_card, page_header

def show_beranda(df, metrics):
    page_header(
        "ParuSehat",
        "Screening risiko paru dari data kesehatan — latih model, evaluasi, konsultasi interaktif.",
    )

    best = metrics[metrics["best_model_key"]]
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Dataset", f"{len(df):,}")
    with c2:
        metric_card("Fitur", "9")
    with c3:
        metric_card("Best F1", f"{best['f1']*100:.1f}%")
    with c4:
        metric_card("Best AUC", f"{best['roc_auc']*100:.1f}%")
    with c5:
        metric_card("Model Terbaik", metrics["best_model"].split()[0])

    st.markdown('<p class="section-title">Pipeline Machine Learning</p>', unsafe_allow_html=True)

    steps = [
        ("📥", "Muat data", "30.000+ baris data paru"),
        ("🔧", "Preprocessing", "Label encoding per kolom"),
        ("✂️", "Split data", "Train 64% · val 16% · test 20%"),
        ("🔍", "Tuning", "GridSearch + validasi 5-fold"),
        ("📈", "Evaluasi", "Akurasi, F1, ROC-AUC"),
        ("🩺", "Konsultasi", "Prediksi + probabilitas live"),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(steps):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="metric-card" style="text-align:left;">
                    <div style="font-size:1.5rem;">{icon}</div>
                    <div style="font-weight:600;color:#0f172a;margin:0.4rem 0;">{title}</div>
                    <div style="font-size:0.85rem;color:#64748b;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<p class="section-title">Algoritma yang Digunakan</p>', unsafe_allow_html=True)
    t1, t2 = st.columns(2)
    with t1:
        m = metrics["dt"]
        st.markdown(
            f"""
            **🌳 Decision Tree**
            - GridSearch: max_depth, min_samples_split, criterion
            - F1 Test: **{m['f1']*100:.2f}%** | ROC-AUC: **{m['roc_auc']*100:.2f}%**
            """
        )
    with t2:
        m = metrics["nb"]
        st.markdown(
            f"""
            **📊 Naive Bayes (Gaussian)**
            - GridSearch: var_smoothing
            - F1 Test: **{m['f1']*100:.2f}%** | ROC-AUC: **{m['roc_auc']*100:.2f}%**
            """
        )

    st.success(f"Model andalan: **{metrics['best_model']}** (F1 tertinggi di data test).")

    st.markdown('<p class="section-title">Distribusi Label</p>', unsafe_allow_html=True)
    chart = df["Hasil"].value_counts().reset_index()
    chart.columns = ["Hasil", "Jumlah"]
    st.bar_chart(chart.set_index("Hasil"))
