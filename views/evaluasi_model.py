import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from modules.ui import label_column, page_header

def show_evaluasi(models, feature_names, metrics):
    page_header(
        "Evaluasi model",
        "Bandingkan Decision Tree vs Naive Bayes — metrik, matriks, kurva ROC.",
    )

    _render_comparison(metrics)

    st.markdown("---")
    tab_dt, tab_nb, tab_roc = st.tabs(
        ["Decision Tree", "Naive Bayes", "Perbandingan ROC"]
    )

    best_key = metrics["best_model_key"]
    with tab_dt:
        _render_model_tab("dt", models["dt"], feature_names, metrics["dt"], best_key)
    with tab_nb:
        _render_model_tab("nb", models["nb"], feature_names, metrics["nb"], best_key)
    with tab_roc:
        _render_roc_comparison(metrics)


def _render_comparison(metrics):
    st.markdown('<p class="section-title">Perbandingan Metrik (Data Test)</p>', unsafe_allow_html=True)

    rows = []
    for key in ["dt", "nb"]:
        m = metrics[key]
        rows.append({
            "Model": m["name"],
            "Akurasi": m["accuracy"],
            "Precision": m["precision"],
            "Recall": m["recall"],
            "F1-Score": m["f1"],
            "ROC-AUC": m["roc_auc"],
            "CV F1 (mean)": m["cv_f1_mean"],
        })
    df_cmp = pd.DataFrame(rows)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.dataframe(
            df_cmp.style.format({
                "Akurasi": "{:.4f}",
                "Precision": "{:.4f}",
                "Recall": "{:.4f}",
                "F1-Score": "{:.4f}",
                "ROC-AUC": "{:.4f}",
                "CV F1 (mean)": "{:.4f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
    with c2:
        chart_df = df_cmp.set_index("Model")[["Akurasi", "F1-Score", "ROC-AUC"]]
        st.bar_chart(chart_df)

    st.info(f"Model andalan: **{metrics['best_model']}** (F1 tertinggi di data test)")


def _render_model_tab(key, model, feature_names, m, best_key):
    badge = " 🏆 Model Terbaik" if key == best_key else ""
    st.markdown(f"### {m['name']}{badge}")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Akurasi", f"{m['accuracy'] * 100:.2f}%")
    c2.metric("Precision", f"{m['precision'] * 100:.2f}%")
    c3.metric("Recall", f"{m['recall'] * 100:.2f}%")
    c4.metric("F1-Score", f"{m['f1'] * 100:.2f}%")
    c5.metric("ROC-AUC", f"{m['roc_auc'] * 100:.2f}%")

    st.markdown("##### Hyperparameter Terbaik")
    st.json(m["best_params"])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### Classification Report (Test)")
        report = m["report"]
        st.dataframe(
            pd.DataFrame({
                "Kelas": ["Tidak (0)", "Ya (1)", "Weighted Avg"],
                "Precision": [
                    report["0"]["precision"],
                    report["1"]["precision"],
                    report["weighted avg"]["precision"],
                ],
                "Recall": [
                    report["0"]["recall"],
                    report["1"]["recall"],
                    report["weighted avg"]["recall"],
                ],
                "F1": [
                    report["0"]["f1-score"],
                    report["1"]["f1-score"],
                    report["weighted avg"]["f1-score"],
                ],
            }).style.format({"Precision": "{:.4f}", "Recall": "{:.4f}", "F1": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
    with c2:
        st.markdown("##### Confusion Matrix (Test)")
        cm_df = pd.DataFrame(
            m["confusion"],
            index=["Aktual: Tidak", "Aktual: Ya"],
            columns=["Pred: Tidak", "Pred: Ya"],
        )
        st.dataframe(cm_df, use_container_width=True)

    if key == "dt":
        st.markdown("##### Feature Importance")
        imp = pd.DataFrame({
            "Fitur": [label_column(f) for f in feature_names],
            "Importance": model.feature_importances_,
        }).sort_values("Importance", ascending=True)
        st.bar_chart(imp.set_index("Fitur"))


def _render_roc_comparison(metrics):
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = {"dt": "#0d9488", "nb": "#6366f1"}

    for key in ["dt", "nb"]:
        m = metrics[key]
        roc = m["roc_curve"]
        ax.plot(
            roc["fpr"],
            roc["tpr"],
            color=colors[key],
            lw=2,
            label=f"{m['name']} (AUC={m['roc_auc']:.4f})",
        )

    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Random Classifier")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve — Perbandingan Model")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)
