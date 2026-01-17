from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os

app = Flask(__name__)

# REQUIRED for session management
app.secret_key = "production-secret-key"

# In-memory storage (production apps use DB)
MESSAGES = []

# Dummy user (for learning purpose)
USERS = {
    "admin": "admin123"
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if USERS.get(username) == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("index.html", error="Invalid credentials")

    return render_template("index.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        message = request.form.get("message")
        if message:
            MESSAGES.append({
                "user": session["user"],
                "message": message,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    return render_template(
        "dashboard.html",
        user=session["user"],
        messages=MESSAGES
    )


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

