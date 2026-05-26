"""Skor risiko klinis + penggabungan dengan prediksi ML."""

USIA_MUDA_MAX = 44
RISIKO_THRESHOLD = 35
RISIKO_TINGGI = 50


def umur_ke_kategori(umur: int) -> str:
    return "Muda" if umur <= USIA_MUDA_MAX else "Tua"


def hitung_bmi(berat_kg: float, tinggi_cm: float) -> float | None:
    if tinggi_cm <= 0 or berat_kg <= 0:
        return None
    tinggi_m = tinggi_cm / 100
    return round(berat_kg / (tinggi_m**2), 1)


def kategori_bmi(bmi: float | None) -> str:
    if bmi is None:
        return "-"
    if bmi < 18.5:
        return "Kurus"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Gemuk"
    return "Obesitas"


def inferensi_status_merokok(lama_tahun: int, batang_hari: int) -> str:
    """Perokok aktif jika ada riwayat merokok terukur."""
    if batang_hari >= 1 or lama_tahun >= 1:
        return "Aktif"
    return "Pasif"


def hitung_pack_years(batang_hari: int, lama_tahun: int) -> float:
    return round((batang_hari * lama_tahun) / 20.0, 1)


def hitung_skor_risiko_klinis(profile: dict, user_input: dict) -> tuple[int, list[str], float]:
    """Skor 0–100 berbasis faktor risiko paru (standar klinis)."""
    score = 0
    faktor = []

    batang = int(profile.get("batang_per_hari", 0) or 0)
    lama = int(profile.get("lama_merokok", 0) or 0)
    umur = int(profile.get("umur", 0) or 0)
    pack_years = hitung_pack_years(batang, lama)

    if batang >= 1 or lama >= 1:
        score += 12
        faktor.append(f"Merokok {lama} th · {batang} batang/hari")

    if batang >= 3:
        score += 18
        faktor.append("Paparan tinggi (≥3 batang/hari)")
    if batang >= 6:
        score += 22
        faktor.append("Perokok berat (≥6 batang/hari)")

    if lama >= 5:
        score += 15
    if lama >= 10:
        score += 25
        faktor.append(f"Lama merokok ≥10 th (pack-years ≈ {pack_years})")

    if pack_years >= 5:
        score += 20
        faktor.append(f"Pack-years tinggi ({pack_years})")

    if user_input.get("Merokok") == "Aktif":
        score += 8

    if user_input.get("Penyakit_Bawaan") == "Ada":
        score += 22
        faktor.append("Ada penyakit bawaan")

    if umur >= 45:
        score += 12
        faktor.append(f"Umur {umur} th (≥45)")

    if user_input.get("Aktivitas_Olahraga") == "Jarang":
        score += 8

    if user_input.get("Aktivitas_Begadang") == "Ya":
        score += 6

    bmi = profile.get("bmi")
    if bmi and bmi >= 30:
        score += 10
        faktor.append(f"BMI obes ({bmi})")

    if profile.get("keluhan", "").strip():
        score += 10
        faktor.append("Ada keluhan napas atau batuk")

    return min(score, 100), faktor, pack_years


def gabungkan_prediksi(ml_hasil: str, skor_klinis: int, profile: dict, user_input: dict):
    """
    Gabungkan ML + aturan klinis.
    Dataset memiliki kekhususan label Merokok; perokok berat selalu dinaikkan risikonya.
    """
    batang = int(profile.get("batang_per_hari", 0) or 0)
    lama = int(profile.get("lama_merokok", 0) or 0)
    adjusted = False
    alasan = []

    # Aturan keras — perokok berat HARUS risiko tinggi
    if batang >= 6 and lama >= 5:
        return "Ya", True, ["Profil berat: ≥6 batang/hari & ≥5 tahun — risiko dinaikkan"], skor_klinis
    if batang >= 3 and lama >= 3:
        return "Ya", True, ["Rutin merokok: ≥3 batang/hari & ≥3 tahun"], skor_klinis
    if lama >= 10 and batang >= 1:
        return "Ya", True, [f"Lama merokok {lama} th, {batang} batang/hari — risiko tinggi"], skor_klinis
    if batang >= 10:
        return "Ya", True, ["Konsumsi sangat tinggi (≥10 batang/hari)"], skor_klinis

    if skor_klinis >= RISIKO_TINGGI:
        alasan.append(f"Skor risiko klinis tinggi ({skor_klinis}/100)")
        return "Ya", ml_hasil != "Ya", alasan, skor_klinis

    if ml_hasil == "Ya" or skor_klinis >= RISIKO_THRESHOLD:
        if ml_hasil != "Ya" and skor_klinis >= RISIKO_THRESHOLD:
            adjusted = True
            alasan.append(
                f"Skor klinis {skor_klinis}/100 menggeser hasil "
                f"(ML awal: {ml_hasil})"
            )
        return "Ya", adjusted, alasan, skor_klinis

    return "Tidak", False, alasan, skor_klinis


def saran_klinis_ringkas(hasil: str, umur: int, merokok: str, penyakit_bawaan: str, profile: dict) -> str:
    tips = []
    batang = int(profile.get("batang_per_hari", 0) or 0)
    lama = int(profile.get("lama_merokok", 0) or 0)

    if hasil == "Ya":
        tips.append("Worth it ke **dokter paru** — rontgen atau spirometri biar jelas kondisinya.")
    if batang >= 3 or lama >= 3:
        tips.append(
            f"Quit atau kurangi dulu — {lama} tahun × {batang} batang/hari "
            f"buat paru kerja ekstra."
        )
    elif merokok == "Aktif":
        tips.append("Kalau masih nyerup, coba turunkan bertahap — paru bakal berterima kasih.")
    if penyakit_bawaan == "Ada":
        tips.append("Penyakit bawaan perlu kontrol rutin bareng dokter.")
    if umur >= 45:
        tips.append(f"Umur {umur} th — skrining paru tahunan oke banget.")
    if not tips:
        tips.append("Pola hidupmu oke — pertahankan dan cek kesehatan tahunan.")
    return " ".join(tips)
