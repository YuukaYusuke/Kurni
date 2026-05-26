from modules.consultation import gabungkan_prediksi, hitung_skor_risiko_klinis
from modules.features import numeric_to_dataframe


def predict_with_proba(model, input_df):
    pred = int(model.predict(input_df)[0])
    proba = model.predict_proba(input_df)[0]
    return pred, proba


def predict_hybrid(model, numeric_values: dict, profile: dict, user_input: dict):
    """Prediksi dari fitur numerik (range) + koreksi klinis."""
    input_df = numeric_to_dataframe(numeric_values)
    pred_code, proba = predict_with_proba(model, input_df)

    label_order = list(model.classes_)
    # classes_ are 0,1 for Ya/Tidak - 1 = Ya risk
    ml_hasil = "Ya" if pred_code == 1 else "Tidak"
    proba_map = {"Tidak": float(proba[0]), "Ya": float(proba[1])}

    skor, faktor, pack_years = hitung_skor_risiko_klinis(profile, user_input)
    hasil_final, adjusted, alasan, skor = gabungkan_prediksi(
        ml_hasil, skor, profile, user_input
    )

    if adjusted and hasil_final == "Ya":
        proba_map = {"Tidak": 0.25, "Ya": 0.75}
    elif adjusted and hasil_final == "Tidak":
        proba_map = {"Tidak": 0.75, "Ya": 0.25}

    return {
        "hasil": hasil_final,
        "ml_hasil": ml_hasil,
        "proba": proba_map,
        "skor_klinis": skor,
        "faktor_risiko": faktor,
        "pack_years": pack_years,
        "adjusted": adjusted,
        "alasan_koreksi": alasan,
        "numeric_input": numeric_values,
    }
