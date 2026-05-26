"""Visualisasi paru-paru interaktif — menghitam & rusak sesuai input merokok."""


def hitung_kerusakan_paru(lama_tahun: int, batang_hari: int) -> int:
    """Skor kerusakan 0–100 — sensitif (selaras formula widget JS)."""
    return int(round(hitung_kerusakan_float(lama_tahun, batang_hari)))


def hitung_kerusakan_float(lama_tahun: int, batang_hari: int) -> float:
    if batang_hari < 1 and lama_tahun < 1:
        return 0.0
    return min(100.0, batang_hari * 3.25 + lama_tahun * 1.65 + (batang_hari * lama_tahun) * 0.048)


def _status_label(damage: int) -> tuple[str, str]:
    if damage == 0:
        return "Sehat", "#059669"
    if damage < 30:
        return "Ringan terpapar", "#ca8a04"
    if damage < 60:
        return "Rusak sedang", "#ea580c"
    if damage < 85:
        return "Rusak berat", "#dc2626"
    return "Kritis", "#7f1d1d"


def render_lung_visual(lama_tahun: int, batang_hari: int) -> str:
    d = hitung_kerusakan_paru(lama_tahun, batang_hari)
    label, label_color = _status_label(d)

    # Interpolasi warna sehat → hitam
    t = d / 100.0
    r1 = int(252 * (1 - t) + 31 * t)
    g1 = int(165 * (1 - t) + 41 * t)
    b1 = int(165 * (1 - t) + 41 * t)
    r2 = int(244 * (1 - t) + 15 * t)
    g2 = int(114 * (1 - t) + 15 * t)
    b2 = int(182 * (1 - t) + 15 * t)
    color1 = f"rgb({r1},{g1},{b1})"
    color2 = f"rgb({r2},{g2},{b2})"

    brightness = round(1.0 - t * 0.55, 2)
    saturate = round(1.0 - t * 0.85, 2)
    overlay_opacity = round(t * 0.75, 2)
    crack_opacity = round(max(0, (t - 0.25) * 1.4), 2)
    smoke_opacity = round(max(0, (t - 0.1) * 0.9), 2)
    pulse = "lung-pulse" if d == 0 else ""

    return f"""
    <div class="lung-visual-wrap">
        <div class="lung-visual-title">🫁 Kondisi Paru (live)</div>
        <div class="lung-status" style="color:{label_color};border-color:{label_color}40;
            background:{label_color}15;">{label} · {d}% kerusakan</div>
        <div class="lung-svg-box {pulse}">
            <svg viewBox="0 0 200 220" class="lung-svg" style="
                filter: brightness({brightness}) saturate({saturate});
                transition: filter 0.9s ease;
            ">
                <defs>
                    <linearGradient id="lungGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:{color1};transition:stop-color 0.9s"/>
                        <stop offset="100%" style="stop-color:{color2};transition:stop-color 0.9s"/>
                    </linearGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2" result="blur"/>
                        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                </defs>
                <!-- Paru kiri -->
                <path class="lung-tissue" fill="url(#lungGrad)" stroke="#9f1239" stroke-width="1.2"
                    d="M88 45 C55 45 35 75 38 110 C40 145 55 175 78 185 C82 160 80 130 85 100
                       C88 75 92 58 88 45 Z"/>
                <!-- Paru kanan -->
                <path class="lung-tissue" fill="url(#lungGrad)" stroke="#9f1239" stroke-width="1.2"
                    d="M112 45 C145 45 165 75 162 110 C160 145 145 175 122 185 C118 160 120 130
                       115 100 C112 75 108 58 112 45 Z"/>
                <!-- Bronkus -->
                <path fill="none" stroke="#be123c" stroke-width="4" stroke-linecap="round"
                    d="M100 30 L100 55 M100 55 L78 70 M100 55 L122 70"
                    style="opacity:{round(1-t*0.5,2)};transition:opacity 0.9s"/>
                <!-- Lapisan hitam (kerusakan) -->
                <g class="damage-overlay" style="opacity:{overlay_opacity};transition:opacity 0.9s ease">
                    <path fill="#1c1917" d="M88 45 C55 45 35 75 38 110 C40 145 55 175 78 185
                       C82 160 80 130 85 100 C88 75 92 58 88 45 Z"/>
                    <path fill="#0c0a09" d="M112 45 C145 45 165 75 162 110 C160 145 145 175 122 185
                       C118 160 120 130 115 100 C112 75 108 58 112 45 Z"/>
                </g>
                <!-- Retak / rusak -->
                <g class="cracks" style="opacity:{crack_opacity};transition:opacity 0.9s ease">
                    <path fill="none" stroke="#44403c" stroke-width="1.5"
                        d="M55 95 L70 120 L62 150 M60 110 L48 130"/>
                    <path fill="none" stroke="#292524" stroke-width="1.2"
                        d="M145 90 L130 115 L138 155 M140 105 L152 128"/>
                    <path fill="none" stroke="#57534e" stroke-width="1"
                        d="M90 130 L100 145 L95 165 M110 128 L100 148 L108 168"/>
                </g>
            </svg>
            <!-- Asap -->
            <div class="smoke-layer" style="opacity:{smoke_opacity}">
                <div class="smoke s1"></div>
                <div class="smoke s2"></div>
                <div class="smoke s3"></div>
            </div>
        </div>
        <div class="lung-hint">
            Geser slider → paru berubah perlahan
            {f"({batang_hari} btg · {lama_tahun} th)" if d > 0 else ""}
        </div>
    </div>
    <style>
    .lung-visual-wrap {{
        text-align:center;padding:0.5rem;
        background:linear-gradient(180deg,#f8fafc,#f1f5f9);
        border-radius:16px;border:1px solid #e2e8f0;
        min-height:320px;
    }}
    .lung-visual-title {{
        font-weight:700;color:#0f766e;font-size:0.95rem;margin-bottom:0.4rem;
    }}
    .lung-status {{
        display:inline-block;font-size:0.8rem;font-weight:600;
        padding:4px 12px;border-radius:20px;border:1px solid;
        margin-bottom:0.5rem;transition:all 0.8s ease;
    }}
    .lung-svg-box {{
        position:relative;display:inline-block;margin:0 auto;
    }}
    .lung-svg {{
        width:180px;height:auto;display:block;
        transition:filter 0.9s ease;
    }}
    .lung-tissue {{
        transition: fill 0.9s ease;
    }}
    .lung-pulse .lung-tissue {{
        animation: lungPulse 2.5s ease-in-out infinite;
    }}
    @keyframes lungPulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.02); }}
    }}
    .smoke-layer {{
        position:absolute;bottom:20%;left:50%;transform:translateX(-50%);
        width:120px;height:80px;pointer-events:none;
        transition:opacity 0.9s ease;
    }}
    .smoke {{
        position:absolute;bottom:0;width:24px;height:24px;
        background:radial-gradient(circle,#78716c 0%,transparent 70%);
        border-radius:50%;opacity:0.6;
        animation: smokeRise 3s ease-out infinite;
    }}
    .smoke.s1 {{ left:20%; animation-delay:0s; }}
    .smoke.s2 {{ left:45%; animation-delay:1s; width:32px;height:32px; }}
    .smoke.s3 {{ left:65%; animation-delay:2s; }}
    @keyframes smokeRise {{
        0% {{ transform:translateY(0) scale(0.6); opacity:0; }}
        30% {{ opacity:0.5; }}
        100% {{ transform:translateY(-70px) scale(1.4); opacity:0; }}
    }}
    .lung-hint {{
        font-size:0.72rem;color:#64748b;margin-top:0.5rem;
    }}
    </style>
    """
