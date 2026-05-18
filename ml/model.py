"""
AI Sleep Disorder Detection - ML Model
Uses Random Forest Classifier trained on smartphone sensor data
Features: movement (m/s²), noise (dB), screen usage (0/1)
Labels:  Normal Sleep, Insomnia, Poor Sleep Habit, Restless Sleep
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os, pickle, warnings
warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "sleep_data2.csv")
MODEL_PATH = os.path.join(BASE_DIR, "ml", "sleep_model.pkl")

# ─── Label generation rules ───────────────────────────────────────────────────
def label_disorder(row):
    mov = row["movement"]
    noise = row["noise"]
    screen = row["screen"]
    if mov > 20 and noise > 0:
        return "Insomnia"
    if mov > 18 and screen == 1:
        return "Poor Sleep Habit"
    if mov < 12 and noise == 0:
        return "Normal Sleep"
    return "Restless Sleep"

# ─── Sleep score formula ──────────────────────────────────────────────────────
def compute_sleep_score(movement, noise, screen):
    """Higher score = better sleep. 0–100 scale."""
    mov_norm = min(movement / 55.0, 1.0)   # higher movement → worse
    noise_norm = min(noise / 100.0, 1.0)   # higher noise → worse
    screen_penalty = 0.15 if screen == 1 else 0.0

    score = 100 - (mov_norm * 50) - (noise_norm * 30) - (screen_penalty * 100)
    score = max(5, min(100, round(score)))
    return int(score)

# ─── Train model ─────────────────────────────────────────────────────────────
def train_model():
    df = pd.read_csv(DATA_PATH)
    df["movement"] = pd.to_numeric(df["movement"], errors="coerce")
    df["noise"] = pd.to_numeric(df["noise"], errors="coerce")
    df["screen"] = pd.to_numeric(df["screen"], errors="coerce")
    df.dropna(inplace=True)

    # Add augmented diversity for balanced training
    extra_rows = []
    for mov, noise, scr, lbl in [
        (35.0, 60.0, 0, "Insomnia"),
        (28.0, 45.0, 0, "Insomnia"),
        (40.0, 70.0, 1, "Insomnia"),
        (22.0, 5.0,  1, "Poor Sleep Habit"),
        (19.0, 2.0,  1, "Poor Sleep Habit"),
        (25.0, 0.0,  1, "Poor Sleep Habit"),
        (8.0,  0.0,  0, "Normal Sleep"),
        (5.0,  0.0,  0, "Normal Sleep"),
        (11.0, 0.0,  0, "Normal Sleep"),
        (15.0, 0.0,  0, "Restless Sleep"),
        (16.0, 2.0,  0, "Restless Sleep"),
        (17.0, 1.0,  0, "Restless Sleep"),
    ] * 40:
        extra_rows.append({"movement": mov, "noise": noise, "screen": scr})

    df_aug = pd.DataFrame(extra_rows)
    df_aug["disorder"] = [r[3] for r in [
        (35.0, 60.0, 0, "Insomnia"),
        (28.0, 45.0, 0, "Insomnia"),
        (40.0, 70.0, 1, "Insomnia"),
        (22.0, 5.0,  1, "Poor Sleep Habit"),
        (19.0, 2.0,  1, "Poor Sleep Habit"),
        (25.0, 0.0,  1, "Poor Sleep Habit"),
        (8.0,  0.0,  0, "Normal Sleep"),
        (5.0,  0.0,  0, "Normal Sleep"),
        (11.0, 0.0,  0, "Normal Sleep"),
        (15.0, 0.0,  0, "Restless Sleep"),
        (16.0, 2.0,  0, "Restless Sleep"),
        (17.0, 1.0,  0, "Restless Sleep"),
    ] * 40]

    df["disorder"] = df.apply(label_disorder, axis=1)
    df_all = pd.concat([df[["movement","noise","screen","disorder"]], df_aug], ignore_index=True)

    X = df_all[["movement", "noise", "screen"]].values
    y = df_all["disorder"].values

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
    clf.fit(X_train, y_train)

    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"[ML] Model trained. Accuracy: {acc:.2%}")

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": clf, "encoder": le}, f)
    return clf, le

# ─── Load or train ────────────────────────────────────────────────────────────
def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            data = pickle.load(f)
        return data["model"], data["encoder"]
    return train_model()

# ─── Predict ─────────────────────────────────────────────────────────────────
def predict(movement, noise, screen):
    clf, le = load_model()
    X = np.array([[float(movement), float(noise), int(screen)]])
    pred_enc = clf.predict(X)[0]
    proba = clf.predict_proba(X)[0]
    label = le.inverse_transform([pred_enc])[0]
    confidence = round(float(max(proba)) * 100, 1)
    score = compute_sleep_score(float(movement), float(noise), int(screen))
    return {
        "disorder": label,
        "score": score,
        "confidence": confidence,
        "probabilities": dict(zip(le.classes_, [round(p*100,1) for p in proba]))
    }

# ─── Weekly analytics from CSV ───────────────────────────────────────────────
def get_weekly_data():
    df = pd.read_csv(DATA_PATH)
    df["movement"] = pd.to_numeric(df["movement"], errors="coerce")
    df["noise"] = pd.to_numeric(df["noise"], errors="coerce")
    df["screen"] = pd.to_numeric(df["screen"], errors="coerce")
    df.dropna(inplace=True)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    chunk = len(df) // 7
    result = []
    for i in range(7):
        chunk_df = df.iloc[i*chunk:(i+1)*chunk]
        mov = round(chunk_df["movement"].mean(), 2)
        noise = round(chunk_df["noise"].mean(), 2)
        scr = round(chunk_df["screen"].mean(), 2)
        disorder = label_disorder({"movement": mov, "noise": noise, "screen": scr})
        score = compute_sleep_score(mov, noise, 1 if scr > 0.3 else 0)
        result.append({
            "day": days[i], "movement": mov, "noise": noise,
            "screen": round(scr * 100, 1), "disorder": disorder, "score": score
        })
    return result

if __name__ == "__main__":
    train_model()
    print(predict(10.3, 0, 0))
    print(predict(35.0, 60.0, 1))
