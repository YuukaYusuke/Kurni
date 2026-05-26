import random

import streamlit as st
from modules.consultation import (
    hitung_bmi,
    inferensi_status_merokok,
    kategori_bmi,
    saran_klinis_ringkas,
    umur_ke_kategori,
)
from modules.features import RANGES, compare_to_benchmark, profile_to_numeric
from modules.lung_component import render_lung_widget
from modules.lung_visual import hitung_kerusakan_paru
from modules.predict import predict_hybrid
from modules.quit_services import show_layanan_berhenti_merokok, show_quit_tips_and_layanan
from modules.smoking_tiers import (
    get_tier_pesan,
    hitung_tier_progress,
    klasifikasi_tier_merokok,
    render_tier_alert_html,
)
from modules.ui import FEATURE_HELP, MODEL_INFO, label_column, page_header

PUNCHLINE_RISIKO = [
    "🔥 Menyala paru paruku!",
    "🚬 Dud ra mati, mending dud ra tekan mati",
    "💀 Udud og ilegal muas",
]
PUNCHLINE_AMAN = [
    "😊 Ra udud ra smile~",
    "✨ Paru tenang — napas lega",
    "🫁 Ngakak paru paruku",
]


def _punchline_hasil(hasil: str, profile: dict) -> str:
    """Pilih punchline acak; jika perokok + risiko, kadang gabung quote tier."""
    if hasil == "Ya":
        joke = random.choice(PUNCHLINE_RISIKO)
        if profile.get("smoking_tier") and profile.get("smoking_quote"):
            if random.choice([True, False]):
                joke += (
                    f'<br><small>tier {profile["smoking_tier"]}: '
                    f'<em>"{profile["smoking_quote"]}"</em></small>'
                )
        return joke
    return random.choice(PUNCHLINE_AMAN)

OTHER_FEATURES = [
    c for c in [
        "Bekerja", "Rumah_Tangga", "Aktivitas_Begadang",
        "Aktivitas_Olahraga", "Asuransi", "Penyakit_Bawaan",
    ]
]


def show_prediksi(models, df, encoders, metrics, benchmarks):
    page_header(
        "Konsultasi & Diagnosis",
        "Isi data kamu — geser slider, lihat paru berubah, lalu jalankan diagnosis.",
    )

    st.markdown(
        f"""
        <div class="info-box">
        Model latih dari <strong>{metrics.get('raw_samples', 0):,}</strong> sampel
        → <strong>{metrics.get('augmented_samples', 0):,}</strong> setelah augmentasi range.
        Inputmu dibandingin ke pola umum di dataset (min–max, persentil).
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="section-title">1 · Pilih model</p>', unsafe_allow_html=True)
    model_choice = st.radio("Algoritma", list(MODEL_INFO.keys()), horizontal=True)
    info = MODEL_INFO[model_choice]
    m = metrics[info["key"]]
    st.caption(f"F1 di test: {m['f1']*100:.1f}% · Rekomendasi sistem: {metrics.get('best_model', '-')}")

    st.markdown("---")
    st.markdown('<p class="section-title">2 · Data kamu</p>', unsafe_allow_html=True)

    profile = {}
    c1, c2, c3 = st.columns(3)
    with c1:
        profile["nama"] = st.text_input("Nama", placeholder="Budi")
        profile["umur"] = st.slider(
            "Umur (tahun)", RANGES["umur"][0], RANGES["umur"][1], 25,
            help=f"Range latih: {RANGES['umur'][0]}–{RANGES['umur'][1]}",
        )
    with c2:
        profile["jenis_kelamin"] = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        profile["tinggi_cm"] = st.number_input("Tinggi (cm)", 100, 220, 170)
    with c3:
        profile["berat_kg"] = st.number_input("Berat (kg)", 30, 200, 65)
        profile["bmi"] = hitung_bmi(profile["berat_kg"], profile["tinggi_cm"])
        profile["bmi_kategori"] = kategori_bmi(profile["bmi"])
        if profile["bmi"]:
            st.metric("BMI", profile["bmi"], profile["bmi_kategori"])

    kategori_usia = umur_ke_kategori(int(profile["umur"]))
    st.caption(f"Umur {profile['umur']} th → kelompok di dataset: **{kategori_usia}**")

    st.markdown("---")
    st.markdown(
        '<p class="section-title">3 · Riwayat rokok & simulasi paru</p>',
        unsafe_allow_html=True,
    )

    col_paru, col_input = st.columns([1.05, 1])

    with col_paru:
        lung_vals = render_lung_widget(
            batang=st.session_state.get("lung_batang_slider", 0),
            lama=st.session_state.get("lung_lama_slider", 0),
            key="lung",
        )
        profile["batang_per_hari"] = lung_vals["batang"]
        profile["lama_merokok"] = lung_vals["lama"]
        st.caption("Paru di atas ikut napas · slider bawah = nilai untuk diagnosis")

    with col_input:
        profile["keluhan"] = st.text_area(
            "Keluhan napas / batuk", height=180,
            placeholder="Contoh: sesak, batuk lama, nyeri dada…",
        )
        st.caption(
            f"**{profile['lama_merokok']} th** · **{profile['batang_per_hari']} batang/hari** · "
            f"estimasi kerusakan paru **{hitung_kerusakan_paru(profile['lama_merokok'], profile['batang_per_hari'])}%**"
        )

    lama = int(profile["lama_merokok"])
    batang = int(profile["batang_per_hari"])
    profile["lung_damage"] = hitung_kerusakan_paru(lama, batang)
    merokok_auto = inferensi_status_merokok(lama, batang)

    # Sidebar badge (live update)
    tier_key = klasifikasi_tier_merokok(lama, batang)
    st.session_state["is_smoker"] = tier_key is not None
    st.session_state["smoking_tier"] = tier_key

    # Progress bar live menuju tier berikutnya
    prog, prog_tier, prog_label = hitung_tier_progress(lama, batang)
    st.markdown("##### 📶 Paparan rokok (live)")
    st.progress(prog, text=prog_label)
    if tier_key is None:
        st.success("✨ **Paru sehat** — belum ada riwayat rokok. *Ra udud ra smile~*")

    if tier_key:
        tier_pesan = get_tier_pesan(
            tier_key, lama, batang, int(profile.get("umur", 0))
        )
        profile["smoking_tier"] = tier_key
        profile["smoking_quote"] = tier_pesan["quote"]
        st.markdown(render_tier_alert_html(tier_pesan), unsafe_allow_html=True)

        # Tierlist visual
        st.markdown("##### 🎮 Tierlist perokok")
        tcols = st.columns(3)
        tier_labels = {
            "ringan": ("C · Ringan", "langkah 76 apel"),
            "sedang": ("B · Sedang", "napas surya"),
            "berat": ("S · Berat", "rokoknya pasti ilegal"),
        }
        for col, tkey in zip(tcols, ["ringan", "sedang", "berat"]):
            active = tkey == tier_key
            title, quote = tier_labels[tkey]
            with col:
                st.markdown(
                    f"""
                    <div style="
                        text-align:center;padding:0.65rem;border-radius:10px;
                        background:{'#0f766e' if active else '#ffffff'};
                        color:{'#ffffff' if active else '#334155'};
                        font-weight:{'700' if active else '500'};
                        border:{'2px solid #0d9488' if active else '1px solid #cbd5e1'};
                        box-shadow:{'0 4px 12px rgba(15,118,110,0.25)' if active else 'none'};
                    ">
                        <div>{title}</div>
                        <div style="
                            font-size:0.72rem;font-style:italic;margin-top:0.35rem;
                            color:{'#ccfbf1' if active else '#64748b'};
                        ">"{quote}"</div>
                        <small style="color:{'#99f6e4' if active else '#94a3b8'};">
                            {'← posisimu' if active else ''}
                        </small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        show_quit_tips_and_layanan(tier_key)
    elif lama < 1 and batang < 1:
        with st.expander("💚 Jaga paru tetap hijau", expanded=False):
            st.write("Pertahankan bebas rokok. Kalau ada keluarga yang masih nyerup, ajak ke KBM — mereka juga butuh teman.")

    st.markdown('<p class="section-title">4 · Faktor lain</p>', unsafe_allow_html=True)

    user_input = {
        "Usia": kategori_usia,
        "Jenis_Kelamin": profile["jenis_kelamin"],
        "Merokok": merokok_auto,
    }

    cols = st.columns(2)
    merokok_opts = sorted(df["Merokok"].unique().tolist())
    with cols[0]:
        user_input["Merokok"] = st.selectbox(
            "Status Merokok", merokok_opts,
            index=merokok_opts.index(merokok_auto) if merokok_auto in merokok_opts else 0,
        )
    for i, col in enumerate(OTHER_FEATURES):
        with cols[(i + 1) % 2]:
            user_input[col] = st.selectbox(
                label_column(col), sorted(df[col].unique().tolist()),
                help=FEATURE_HELP.get(col, ""), key=f"in_{col}",
            )

    numeric_values = profile_to_numeric(profile, user_input)
    tolok_ukur = compare_to_benchmark(numeric_values, benchmarks)

    with st.expander("📊 Bandingkan dengan dataset", expanded=True):
        if tolok_ukur:
            for t in tolok_ukur:
                st.markdown(
                    f"**{t['fitur']}**: {t['nilai']} — {t['level']} "
                    f"(range dataset: {t['range_dataset']}, rata-rata: {t['rata_rata']})"
                )
        st.caption(
            f"{benchmarks['_meta']['total_samples']:,} sampel di dataset · "
            f"{benchmarks['_meta']['risk_positive_rate']*100:.1f}% berlabel risiko (Ya) di data latih"
        )

    st.markdown("---")
    if st.button("🔬 Jalankan diagnosis", type="primary", use_container_width=True):
        model = models["dt"] if model_choice == "Decision Tree" else models["nb"]
        result = predict_hybrid(model, numeric_values, profile, user_input)
        result["model"] = model_choice
        result["input"] = user_input
        result["profile"] = profile
        result["tolok_ukur"] = tolok_ukur
        if tier_key:
            result["smoking_tier"] = tier_key
            result["smoking_quote"] = profile.get("smoking_quote", "")
        st.session_state.history.append(result)
        st.session_state.last_diagnosis = result
        st.rerun()

    if "last_diagnosis" in st.session_state:
        _render_result(st.session_state.last_diagnosis)


def _render_result(d):
    hasil = d["hasil"]
    profile = d.get("profile", {})
    user_input = d.get("input", {})
    nama = profile.get("nama") or "Pasien"

    st.markdown('<p class="section-title">Hasil diagnosis</p>', unsafe_allow_html=True)

    joke = _punchline_hasil(hasil, profile)
    st.markdown(
        f'<div style="text-align:center;padding:0.75rem;border-radius:12px;'
        f'border:2px dashed {"#f59e0b" if hasil == "Ya" else "#10b981"};'
        f'font-size:1.05rem;">{joke}</div>',
        unsafe_allow_html=True,
    )

    skor = d.get("skor_klinis", 0)
    st.markdown("##### Skor risiko klinis")
    st.progress(skor / 100, text=f"{skor}/100")
    for f in d.get("faktor_risiko", []):
        st.markdown(f"- {f}")

    if d.get("adjusted") or d.get("ml_hasil") != hasil:
        st.warning(f"ML: **{d.get('ml_hasil')}** → Final: **{hasil}** (koreksi range/klinis)")
        for a in d.get("alasan_koreksi", []):
            st.markdown(f"- {a}")

    if d.get("tolok_ukur"):
        st.markdown("##### Posisi di dataset")
        for t in d["tolok_ukur"]:
            st.caption(f"{t['fitur']}: {t['nilai']} — {t['level']}")

    if d.get("proba"):
        st.markdown("##### Probabilitas")
        for label, p in d["proba"].items():
            st.progress(p, text=f"{label}: {p*100:.1f}%")

    css = "result-positive" if hasil == "Ya" else "result-negative"
    color = "#b91c1c" if hasil == "Ya" else "#15803d"
    label = "Risiko terdeteksi" if hasil == "Ya" else "Risiko rendah"
    st.markdown(
        f'<div class="{css}"><div style="font-size:1.3rem;font-weight:700;color:{color};">{label}</div></div>',
        unsafe_allow_html=True,
    )

    st.write(saran_klinis_ringkas(
        hasil, int(profile.get("umur", 0)),
        user_input.get("Merokok", ""), user_input.get("Penyakit_Bawaan", ""), profile,
    ))
    if profile.get("smoking_tier"):
        show_quit_tips_and_layanan(profile["smoking_tier"])
    elif profile.get("lama_merokok", 0) < 1 and profile.get("batang_per_hari", 0) < 1:
        show_layanan_berhenti_merokok(None, expanded=False)

    st.info(
        "Hasil screening, bukan diagnosis dokter. Kalau ada keluhan, tetap konsultasi langsung.",
        icon="ℹ️",
    )
