import random
import streamlit as st
from modules.ui import label_column, page_header

PUNCHLINE_RISIKO = [
    "🔥 Menyala paru paruku!",
    "Dud ra mati, mending dud ra tekan mati",
    "Udud og ilegal muas",
]
PUNCHLINE_AMAN = [
    "Ra udud ra smile~",
    "Paru tenang — napas lega",
]


def show_history():
    page_header(
        "Riwayat konsultasi",
        "Semua diagnosis sesi ini — nama, skor, dan detail input.",
    )

    history = st.session_state.history

    if not history:
        st.markdown(
            """
            <div class="info-box" style="text-align:center;padding:2rem;">
            Belum ada riwayat.<br>Buka <strong>Konsultasi</strong>, isi data, lalu jalankan diagnosis.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric("Total", len(history))
    with col2:
        if st.button("Hapus semua", use_container_width=True):
            st.session_state.history = []
            if "last_diagnosis" in st.session_state:
                del st.session_state.last_diagnosis
            st.rerun()

    for i, item in enumerate(reversed(history), start=1):
        hasil = item["hasil"]
        icon = "🔴" if hasil == "Ya" else "🟢"
        profile = item.get("profile", {})
        nama = profile.get("nama") or f"Sesi #{len(history) - i + 1}"
        umur = profile.get("umur", "")

        with st.expander(f"{icon} {nama} — {hasil} ({umur} th) · {item['model']}", expanded=(i == 1)):
            joke = random.choice(PUNCHLINE_RISIKO if hasil == "Ya" else PUNCHLINE_AMAN)
            st.caption(joke)

            st.markdown(f"**Model:** {item['model']} · **Hasil:** {hasil}")

            if item.get("smoking_tier"):
                st.caption(
                    f"Tier **{item['smoking_tier'].upper()}** — "
                    f'"{item.get("smoking_quote", "")}"'
                )

            if profile:
                st.markdown(
                    f"**Umur:** {profile.get('umur', '-')} th · "
                    f"**BMI:** {profile.get('bmi', '-')} ({profile.get('bmi_kategori', '-')}) · "
                    f"**JK:** {profile.get('jenis_kelamin', '-')}"
                )

            if "skor_klinis" in item:
                st.markdown(f"**Skor klinis:** {item['skor_klinis']}/100")
            if item.get("adjusted"):
                st.warning(f"ML **{item.get('ml_hasil')}** → akhir **{item['hasil']}** (skor klinis)")
            if "proba" in item:
                for label, p in item["proba"].items():
                    st.progress(p, text=f"{label}: {p*100:.1f}%")

            features = list(item["input"].items())
            mid = (len(features) + 1) // 2
            c1, c2 = st.columns(2)
            with c1:
                for col, val in features[:mid]:
                    st.markdown(f"**{label_column(col)}:** {val}")
            with c2:
                for col, val in features[mid:]:
                    st.markdown(f"**{label_column(col)}:** {val}")
