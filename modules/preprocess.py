from sklearn.preprocessing import LabelEncoder

FEATURE_COLUMNS = [
    "Usia",
    "Jenis_Kelamin",
    "Merokok",
    "Bekerja",
    "Rumah_Tangga",
    "Aktivitas_Begadang",
    "Aktivitas_Olahraga",
    "Asuransi",
    "Penyakit_Bawaan",
]

TARGET_COLUMN = "Hasil"


def preprocess_data(df):
    df_processed = df.copy()
    encoders = {}

    for col in df_processed.columns:
        if df_processed[col].dtype == "object":
            le = LabelEncoder()
            df_processed[col] = le.fit_transform(df_processed[col])
            encoders[col] = le

    return df_processed, encoders


def encode_input(user_input, encoders):
    encoded = {}
    for col, value in user_input.items():
        encoded[col] = int(encoders[col].transform([value])[0])
    return encoded


def decode_label(encoder, value):
    return encoder.inverse_transform([int(value)])[0]
