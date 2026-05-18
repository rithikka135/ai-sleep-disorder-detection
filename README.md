# 🌙 AI-Based Sleep Disorder Detection System

A full-stack web application that analyzes sleep patterns using smartphone sensor data
(phone movement, environmental noise, screen usage) and predicts sleep disorders using
a trained **Random Forest Classifier**.

---

## 📋 Detected Disorders

| Disorder | Trigger Conditions |
|---|---|
| **Normal Sleep** | Low movement + quiet environment |
| **Insomnia** | High movement + high noise |
| **Poor Sleep Habit** | High movement + screen active |
| **Restless Sleep** | Moderate movement, mixed signals |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Copy your sensor CSV
Place `sleep_data2.csv` in the project root (already included).

### 3. Run the app
```bash
python app.py
```

### 4. Open browser
```
http://localhost:5000
```

**Demo credentials:** `demo` / `demo123`

---

## 📁 Project Structure

```
sleep_app/
├── app.py                  # Flask main application
├── requirements.txt
├── sleep_data2.csv         # Real smartphone sensor data
│
├── ml/
│   ├── model.py            # Random Forest ML model + training
│   └── sleep_model.pkl     # Saved trained model (auto-generated)
│
├── database/
│   ├── db.py               # SQLite helpers
│   └── sleep_app.db        # SQLite database (auto-generated)
│
├── templates/
│   ├── base.html           # Base layout + sidebar
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html      # Charts + KPIs
│   ├── analysis.html       # Sensor input + ML prediction
│   ├── history.html        # Sleep records table
│   └── tips.html           # AI recommendations
│
└── static/
    ├── css/style.css       # Full health-themed dark UI
    └── js/main.js          # Chart.js + interactivity
```

---

## 🤖 ML Model Details

- **Algorithm:** Random Forest Classifier (150 trees, max_depth=8)
- **Features:** `movement` (m/s²), `noise` (dB), `screen` (0/1)
- **Training data:** 3,408 real sensor readings + augmented class samples
- **Accuracy:** ~100% on augmented training set
- **Output:** disorder label, sleep score (0–100), confidence %, class probabilities

### Sleep Score Formula
```
score = 100 - (movement_norm × 50) - (noise_norm × 30) - (screen × 15)
```

---

## 🗄️ Database Schema

### `users` table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | Unique username |
| password | TEXT | SHA-256 hashed |
| email | TEXT | Optional |
| created | TIMESTAMP | Registration time |

### `sleep_data` table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | Foreign key to users |
| movement | REAL | Accelerometer reading (m/s²) |
| noise | REAL | Ambient noise level (dB) |
| screen | INTEGER | Screen on (1) or off (0) |
| predicted_disorder | TEXT | ML classification result |
| sleep_score | INTEGER | 0–100 score |
| confidence | REAL | Model confidence % |
| notes | TEXT | User notes |
| recorded_at | TIMESTAMP | Analysis timestamp |

---

## 🌐 Pages & Routes

| Route | Page | Description |
|-------|------|-------------|
| `/` | Index | Redirects to dashboard or login |
| `/login` | Login | User authentication |
| `/register` | Register | New user registration |
| `/dashboard` | Dashboard | KPI cards + 4 charts |
| `/analysis` | Analysis | Sensor input + ML prediction |
| `/history` | History | All past records |
| `/tips` | Tips | AI recommendations by disorder |
| `/logout` | — | Session clear + redirect |
| `/api/predict` | API | POST JSON → prediction |
| `/api/weekly` | API | GET weekly CSV data |
| `/api/stats` | API | GET user statistics |

---

## 🔬 API Usage

```bash
# Predict (POST JSON)
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"movement": 12.5, "noise": 0, "screen": 0}'

# Response:
{
  "disorder": "Normal Sleep",
  "score": 88,
  "confidence": 100.0,
  "probabilities": {
    "Normal Sleep": 100.0,
    "Insomnia": 0.0,
    "Poor Sleep Habit": 0.0,
    "Restless Sleep": 0.0
  }
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3.10+, Flask 3.0 |
| ML | scikit-learn (Random Forest) |
| Database | SQLite 3 |
| Charts | Chart.js 4.4 |
| Fonts | Space Grotesk, JetBrains Mono |
