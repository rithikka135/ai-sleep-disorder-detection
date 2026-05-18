"""
AI-Based Sleep Disorder Detection System
Flask Backend - Main Application
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db, register_user, authenticate_user, get_user, save_sleep_record, get_user_history, get_stats
from ml.model import predict, get_weekly_data, train_model

app = Flask(__name__)
app.secret_key = "sleepsense_ai_secret_2024"

# ── Init ──────────────────────────────────────────────────────────────────────
with app.app_context():
    init_db()
    train_model()  # Pre-train model on startup

# ── Auth helpers ──────────────────────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        if authenticate_user(username, password):
            session["username"] = username
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        confirm  = request.form.get("confirm","").strip()
        email    = request.form.get("email","").strip()
        if not username or not password:
            flash("All fields are required.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
        else:
            ok, msg = register_user(username, password, email)
            if ok:
                flash(msg, "success")
                return redirect(url_for("login"))
            else:
                flash(msg, "error")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    username = session["username"]
    stats = get_stats(username)
    history = get_user_history(username, limit=5)
    weekly = get_weekly_data()
    from datetime import datetime
    return render_template("dashboard.html",
        username=username, stats=stats,
        history=history, weekly=weekly,
        now_hour=datetime.now().hour)

@app.route("/analysis", methods=["GET","POST"])
@login_required
def analysis():
    username = session["username"]
    result = None
    if request.method == "POST":
        try:
            movement = float(request.form.get("movement", 0))
            noise    = float(request.form.get("noise", 0))
            screen   = int(request.form.get("screen", 0))
            notes    = request.form.get("notes","")
            result   = predict(movement, noise, screen)
            save_sleep_record(username, movement, noise, screen,
                              result["disorder"], result["score"],
                              result["confidence"], notes)
        except Exception as e:
            flash(f"Analysis error: {e}", "error")
    return render_template("analysis.html", username=username, result=result)

@app.route("/history")
@login_required
def history():
    username = session["username"]
    records  = get_user_history(username)
    weekly   = get_weekly_data()
    return render_template("history.html", username=username,
                           records=records, weekly=weekly)

@app.route("/tips")
@login_required
def tips():
    return render_template("tips.html", username=session["username"])

# ── API Endpoints (for JS fetch calls) ───────────────────────────────────────
@app.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    data = request.get_json()
    result = predict(data["movement"], data["noise"], data["screen"])
    return jsonify(result)

@app.route("/api/weekly")
@login_required
def api_weekly():
    return jsonify(get_weekly_data())

@app.route("/api/history")
@login_required
def api_history():
    records = get_user_history(session["username"], limit=30)
    return jsonify(records)

@app.route("/api/stats")
@login_required
def api_stats():
    return jsonify(get_stats(session["username"]))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
