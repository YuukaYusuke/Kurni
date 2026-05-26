"""Layanan berhenti merokok — KBM, klan komunitas, gaya peringatan bungkus rokok."""

import html
import streamlit as st

from modules.smoking_tiers import TIERS

# Strip peringatan (ringkas, kayak label di bungkus)
PACK_WARNINGS = [
    "Berhenti sekarang — risiko paru bisa turun",
    "Merokok bikin paru & jantung kerja overtime",
    "Nggak sendirian — ada klan & KBM yang siap bantu",
]

LAYANAN_UTAMA = [
    {
        "peringatan": "Klan komunitas — quit bareng, progress bareng",
        "nama": "Klan / Komunitas",
        "deskripsi": (
            "Teman seperjuangan yang ngerti urge-nya. Meet rutin, grup chat, "
            "dan buddy biar nggak nyerah di minggu pertama."
        ),
        "fitur": ["Meet mingguan", "Grup WA/Telegram", "Buddy system", "Tanpa judge"],
    },
    {
        "peringatan": "KBM terdekat — konseling terarah, peluang quit lebih besar",
        "nama": "Klinik Berhenti Merokok (KBM)",
        "deskripsi": (
            "Di Puskesmas, klinik, atau RS. Tenaga terlatih bantu rencana quit, "
            "terapi nikotin kalau perlu, plus cek paru."
        ),
        "fitur": ["Konseling 1-on-1", "Terapi nikotin", "Rencana bertahap", "Cek paru"],
    },
    {
        "peringatan": "Quitline — curhat anonim, strategi quit tanpa malu",
        "nama": "Quitline & Hotline",
        "deskripsi": "Telepon untuk motivasi dan tips praktis berhenti merokok.",
        "fitur": ["Gratis (layanan pemerintah)", "Anonim", "24 jam (tergantung daerah)"],
    },
    {
        "peringatan": "App quit — hitung hari tanpa rokok + edukasi paru",
        "nama": "Program Digital",
        "deskripsi": "Tracking progress harian, badge, dan artikel singkat soal kesehatan paru.",
        "fitur": ["Reminder", "Badge progress", "Artikel paru"],
    },
]

PROGRAM_TAHAP = [
    ("Minggu 1–2", "Detoks — banyak air, hindari pemicu, minta teman klan/KBM."),
    ("Minggu 3–4", "Urge mulai reda — olahraga ringan, reward yang bukan rokok."),
    ("Bulan 2–3", "Paru mulai recovery — tetap gabung komunitas, cek ke dokter kalau batuk."),
    ("Bulan 6+", "Maintenance — rayakan milestone, jangan lengah."),
]

_PACK_CSS = """<style>
.pack-kbm-wrap .pack-warning-strip {
    background: linear-gradient(165deg, #faf3d4 0%, #e8c96a 55%, #d4a84b 100%);
    border: 2px solid #1a1a1a;
    padding: 12px 14px;
    margin: 8px 0;
    font-family: Georgia, 'Times New Roman', serif;
    text-align: center;
    border-radius: 4px;
    box-shadow: inset 0 0 0 1px rgba(0,0,0,0.08);
}
.pack-kbm-wrap .pack-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: #3d3d3d;
    margin-bottom: 6px;
    text-transform: uppercase;
}
.pack-kbm-wrap .pack-text {
    font-size: 0.92rem;
    font-weight: 800;
    line-height: 1.4;
    color: #111;
    word-wrap: break-word;
}
.pack-kbm-wrap .pack-service-box {
    background: #fffef9;
    border: 3px solid #b91c1c;
    padding: 12px 14px;
    margin: 2px 0 12px 0;
    border-radius: 4px;
}
.pack-kbm-wrap .pack-service-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #991b1b;
    margin-bottom: 6px;
}
.pack-kbm-wrap .pack-service-body {
    font-size: 0.84rem;
    color: #334155;
    line-height: 1.55;
}
.pack-kbm-wrap .pack-service-body em {
    color: #64748b;
    font-style: normal;
    font-size: 0.78rem;
}
.pack-kbm-wrap .pack-roadmap {
    background: #f8fafc;
    border-left: 4px solid #0f766e;
    padding: 10px 12px;
    margin: 6px 0;
    font-size: 0.82rem;
    color: #334155;
    border-radius: 0 8px 8px 0;
}
.pack-kbm-wrap .pack-roadmap strong {
    display: block;
    font-size: 0.75rem;
    color: #0f766e;
    margin-bottom: 4px;
}
.pack-kbm-wrap h4.pack-section-title {
    font-size: 0.95rem;
    margin: 1rem 0 0.4rem 0;
    color: #134e4a;
    font-weight: 600;
}
</style>"""


def _esc(text: str) -> str:
    return html.escape(str(text))


def _pack_strip(text: str, label: str = "Peringatan") -> str:
    return (
        f'<div class="pack-warning-strip">'
        f'<div class="pack-label">{_esc(label)}</div>'
        f'<div class="pack-text">{_esc(text)}</div>'
        f"</div>"
    )


def _pack_service_block(peringatan: str, nama: str, deskripsi: str, fitur: list[str]) -> str:
    fitur_html = " · ".join(f"<b>{_esc(f)}</b>" for f in fitur)
    return (
        f"{_pack_strip(peringatan, 'Layanan quit')}"
        f'<div class="pack-service-box">'
        f'<div class="pack-service-title">{_esc(nama)}</div>'
        f'<div class="pack-service-body">{_esc(deskripsi)}<br><br>'
        f"<em>Isi paket:</em> {fitur_html}</div></div>"
    )


def _build_kbm_html(tier_key: str | None) -> str:
    label_tier = TIERS[tier_key]["label"] if tier_key else "kamu"
    parts = [
        _PACK_CSS,
        '<div class="pack-kbm-wrap">',
        _pack_strip(
            f"Quit lebih gampang kalau ada teman — KBM & klan cocok buat profil {label_tier}",
            "Untuk kamu",
        ),
    ]
    for w in PACK_WARNINGS[:2]:
        parts.append(_pack_strip(w))
    for svc in LAYANAN_UTAMA:
        parts.append(
            _pack_service_block(svc["peringatan"], svc["nama"], svc["deskripsi"], svc["fitur"])
        )
    for w in PACK_WARNINGS[2:]:
        parts.append(_pack_strip(w))
    parts.append('<h4 class="pack-section-title">Jadwal quit (gambaran umum)</h4>')
    for tahap, isi in PROGRAM_TAHAP:
        parts.append(
            f'<div class="pack-roadmap"><strong>{_esc(tahap)}</strong>{_esc(isi)}</div>'
        )
    parts.append(
        _pack_strip(
            "Mulai dari Puskesmas terdekat — tanya KBM atau rujukan poli paru",
            "Langkah pertama",
        )
    )
    parts.append("</div>")
    return "\n".join(parts)


def show_layanan_berhenti_merokok(tier_key: str | None = None, expanded: bool = True):
    with st.expander("🚭 Quit bareng — KBM & klan komunitas", expanded=expanded):
        st.markdown(_build_kbm_html(tier_key), unsafe_allow_html=True)


def show_quit_tips_and_layanan(tier_key: str):
    from modules.smoking_tiers import show_quit_tips

    show_quit_tips(tier_key)
    show_layanan_berhenti_merokok(tier_key, expanded=False)
