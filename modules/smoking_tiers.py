"""
Tierlist perokok — ringan / sedang / berat + quote ikonik.
"""

import random

import streamlit as st

TIERS = {
    "ringan": {
        "label": "Perokok Ringan",
        "tier": "C",
        "badge": "🍃",
        "color": "#ca8a04",
        "bg": "#fffbeb",
        "border": "#fcd34d",
        "quote": "langkah 76 apel",
        "extras": [
            "Paru masih mau diajak ngobrol — quit sekarang paling gampang.",
            "Level C: tutorial mode. Berhenti sekarang = save file.",
        ],
        "serius": "Meski ringan, rokok tetap nambah risiko. Pertimbangkan cuti rokok bertahap.",
    },
    "sedang": {
        "label": "Perokok Sedang",
        "tier": "B",
        "badge": "🌤️",
        "color": "#ea580c",
        "bg": "#fff7ed",
        "border": "#fdba74",
        "quote": "napas surya",
        "extras": [
            "Paru mulai protes — jangan di-AFK terus.",
            "Level B: mid game. Skrining paru worth it kalau ada keluhan.",
        ],
        "serius": "Pola sedang sudah cukup buat cek paru — konsultasi dokter kalau sesak atau batuk lama.",
    },
    "berat": {
        "label": "Perokok Berat",
        "tier": "S",
        "badge": "🔥",
        "color": "#b91c1c",
        "bg": "#fef2f2",
        "border": "#fca5a5",
        "quote": "rokoknya pasti ilegal",
        "quote_alt": ["rokoknya mesti ilegal", "rokoknya pasti ilegal"],
        "extras": [
            "Paru masuk mode boss fight — jangan tunggu game over.",
            "Level S: satu nyawa (kesehatanmu). Prioritas ke dokter paru.",
        ],
        "serius": (
            "Profil berat = risiko tinggi. Segera ke spesialis paru "
            "(rontgen/spirometri jangan ditunda)."
        ),
        "tips_berhenti": [
            "Konsultasi dokter atau KBM — quit cold turkey lebih aman dibimbing.",
            "Ganti ritual: permen, air putih, atau jalan 5 menit pas urge muncul.",
            "Kasih tahu keluarga — dukungan bikin peluang quit naik.",
            "Target cuti rokok bertahap; jangan sendirian kalau batang/hari tinggi.",
            "Cek paru lengkap — rontgen/spirometri sebelum paru makin protes.",
        ],
    },
}

TIPS_BERHENTI = {
    "ringan": [
        "Masih tier ringan — **sekarang** titik terbaik berhenti sebelum naik ke B/S.",
        "Catat pemicu (kopi, stres) dan hindari 2 minggu pertama.",
        "Olahraga 20 menit/hari bantu redain urge.",
        "Grup WA quit-smoking atau app tracking bisa jadi teman.",
    ],
    "sedang": [
        "Boleh coba **patch/komplet nikotin** — konsultasi dokter dulu ya.",
        "Kurangi 1 batang tiap 3 hari (tapering) kalau cold turkey kerasa berat.",
        "Minggu pertama: kurangi ketemu teman yang nyerup — lingkungan penting.",
        "Batuk setelah quit? Sering normal — ke dokter kalau >3 minggu.",
    ],
    "berat": TIERS["berat"]["tips_berhenti"],
}


def klasifikasi_tier_merokok(lama_tahun: int, batang_hari: int) -> str | None:
    if batang_hari < 1 and lama_tahun < 1:
        return None

    pack = (batang_hari * lama_tahun) / 20.0

    if batang_hari >= 15 or lama_tahun >= 20 or (batang_hari >= 10 and lama_tahun >= 10):
        return "berat"
    if batang_hari >= 10 or lama_tahun >= 15 or pack >= 8:
        return "berat"

    if batang_hari >= 5 or lama_tahun >= 5 or pack >= 2:
        return "sedang"

    return "ringan"


def get_tier_pesan(tier_key: str, lama: int, batang: int, umur: int | None = None) -> dict:
    t = TIERS[tier_key]
    quotes = t.get("quote_alt", [t["quote"]])
    main_quote = t["quote"] if tier_key != "berat" else random.choice(quotes)

    return {
        "tier_key": tier_key,
        "tier_rank": t["tier"],
        "label": t["label"],
        "badge": t["badge"],
        "quote": main_quote,
        "extra": random.choice(t["extras"]),
        "serius": t["serius"],
        "color": t["color"],
        "bg": t["bg"],
        "border": t["border"],
        "detail": f"{lama} tahun · {batang} batang/hari",
        "umur": umur,
    }


def hitung_tier_progress(lama_tahun: int, batang_hari: int) -> tuple[float, str | None, str]:
    if batang_hari < 1 and lama_tahun < 1:
        return 0.0, None, "Paru sehat — belum ada riwayat rokok"

    skor = min(batang_hari * 4 + lama_tahun * 1.2, 100)
    tier = klasifikasi_tier_merokok(lama_tahun, batang_hari)

    if tier == "ringan":
        progress = min(skor / 40, 0.95)
        return progress, tier, "Menuju B · sedang → napas surya"
    if tier == "sedang":
        progress = 0.4 + min((skor - 25) / 50, 0.55)
        return min(progress, 0.95), tier, "Menuju S · berat → rokoknya pasti ilegal"
    return 1.0, tier, "Tier S — prioritaskan cek paru"


def render_sidebar_health_badge():
    is_smoker = st.session_state.get("is_smoker")
    tier = st.session_state.get("smoking_tier")

    if is_smoker is False:
        st.sidebar.markdown(
            """
            <div class="sidebar-health-badge" style="
                text-align:center;background:linear-gradient(135deg,#ecfdf5,#d1fae5);
                border:2px solid #34d399;border-radius:12px;
                padding:0.75rem;margin:0.5rem 0;
            ">
                <div style="font-size:1.5rem;color:#047857 !important;">✨</div>
                <div style="font-weight:700;color:#047857 !important;">Paru Sehat</div>
                <div style="font-size:0.75rem;color:#065f46 !important;">Bebas rokok · ra udud ra smile</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif is_smoker and tier:
        t = TIERS[tier]
        quote_color = "#7c2d12" if tier == "sedang" else t["color"]
        st.sidebar.markdown(
            f"""
            <div class="sidebar-health-badge" style="
                text-align:center;background:{t['bg']};
                border:2px solid {t['border']};border-radius:12px;
                padding:0.75rem;margin:0.5rem 0;
                box-shadow:0 2px 8px rgba(0,0,0,0.08);
            ">
                <div style="font-size:1.2rem;color:{t['color']} !important;">{t['badge']} Tier {t['tier']}</div>
                <div style="font-weight:700;color:{t['color']} !important;">{t['label']}</div>
                <div style="
                    font-size:0.85rem;font-weight:600;font-style:italic;
                    color:{quote_color} !important;
                    margin-top:0.35rem;padding:4px 8px;
                    background:rgba(255,255,255,0.7);border-radius:8px;
                ">"{t['quote']}"</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.caption("Isi riwayat rokok di Konsultasi — badge paru bakal muncul di sini")


def show_quit_tips(tier_key: str):
    tips = TIPS_BERHENTI.get(tier_key, [])
    if not tips:
        return
    with st.expander(f"💡 Tips quit — Tier {TIERS[tier_key]['tier']}", expanded=False):
        st.caption(
            f"Untuk **{TIERS[tier_key]['label']}** — saran umum; tetap konsultasi dokter ya."
        )
        for i, tip in enumerate(tips, 1):
            st.markdown(f"{i}. {tip}")


def render_tier_alert_html(pesan: dict) -> str:
    nama_tier = f"Tier {pesan['tier_rank']} · {pesan['label']}"
    return f"""
<div style="
    background:{pesan['bg']};
    border:2px solid {pesan['border']};
    border-radius:16px;
    padding:1.1rem 1.25rem;
    margin:0.75rem 0;
">
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
        <span style="font-size:1.4rem;">{pesan['badge']}</span>
        <span style="font-weight:700;color:{pesan['color']};">{nama_tier}</span>
        <span style="
            background:{pesan['color']};color:white;
            font-size:0.75rem;font-weight:700;
            padding:2px 8px;border-radius:6px;
        ">{pesan['tier_rank']}</span>
    </div>
    <div style="
        font-size:1.15rem;font-weight:700;color:{pesan['color']};margin:0.5rem 0;
        padding:0.5rem 0.75rem;background:rgba(255,255,255,0.85);
        border-radius:10px;border-left:4px solid {pesan['color']};
    ">
        "{pesan['quote']}"
    </div>
    <div style="font-size:0.9rem;color:#475569 !important;font-style:italic;margin-bottom:0.6rem;">
        {pesan['extra']}
    </div>
    <div style="font-size:0.85rem;color:#475569;">
        📋 {pesan['detail']}
        {f" · umur {pesan['umur']} th" if pesan.get('umur') else ""}
    </div>
    <div style="
        margin-top:0.75rem;padding-top:0.75rem;
        border-top:1px dashed {pesan['border']};
        font-size:0.88rem;color:#334155;line-height:1.5;
    ">
        <strong>Yang perlu diingat:</strong> {pesan['serius']}
    </div>
</div>
"""
