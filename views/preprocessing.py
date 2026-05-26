import streamlit as st
from modules.preprocess import FEATURE_COLUMNS, TARGET_COLUMN
from modules.ui import label_column, page_header

def show_preprocessing(df, df_processed, encoders):
    page_header(
        "Dataset & preprocessing",
        "Lihat data mentah dan cara teks diubah jadi angka buat model.",
    )

    tab1, tab2, tab3 = st.tabs(["Data Mentah", "Setelah Preprocessing", "Label Encoding"])

    with tab1:
        st.markdown("##### Preview Dataset")
        c1, c2, c3 = st.columns(3)
        c1.metric("Baris", f"{len(df):,}")
        c2.metric("Kolom", len(df.columns))
        c3.metric("Fitur Prediksi", len(FEATURE_COLUMNS))
        st.dataframe(df.head(15), use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("##### Data Numerik (siap untuk ML)")
        st.dataframe(df_processed.head(15), use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("##### Pemetaan Label Encoding")
        st.markdown(
            '<div class="info-box">Tiap kolom punya encoder sendiri — '
            "teks (misalnya Aktif/Pasif) jadi angka biar model bisa baca.</div>",
            unsafe_allow_html=True,
        )
        mapping_rows = []
        for col in FEATURE_COLUMNS + [TARGET_COLUMN]:
            if col in encoders:
                classes = list(encoders[col].classes_)
                for idx, label in enumerate(classes):
                    mapping_rows.append({
                        "Kolom": label_column(col),
                        "Nilai Asli": label,
                        "Nilai Encoded": idx,
                    })
        st.dataframe(mapping_rows, use_container_width=True, hide_index=True)
