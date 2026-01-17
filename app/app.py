from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
import time
import smtplib
import os
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- DATABASE ----------------
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    email TEXT,
    password TEXT,
    verified INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS otp_verification (
    username TEXT,
    otp TEXT,
    expires_at INTEGER
)
""")

conn.commit()

# ---------------- OTP + EMAIL ----------------
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg.set_content(f"""
Welcome to Omprakash DevOps Learning Platform 🚀

Your OTP is: {otp}
Valid for 5 minutes.
""")

    msg["Subject"] = "Verify your DevOps Account"
    msg["From"] = os.environ.get("SMTP_EMAIL")
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(
            os.environ.get("SMTP_EMAIL"),
            os.environ.get("SMTP_PASSWORD")
        )
        smtp.send_message(msg)

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        conn.commit()

        otp = generate_otp()
        expiry = int(time.time()) + 300

        cursor.execute(
            "INSERT INTO otp_verification VALUES (?, ?, ?)",
            (username, otp, expiry)
        )
        conn.commit()

        send_otp_email(email, otp)
        return redirect(f"/verify/{username}")

    return render_template("register.html")

@app.route("/verify/<username>", methods=["GET", "POST"])
def verify(username):
    if request.method == "POST":
        entered_otp = request.form["otp"]

        cursor.execute(
            "SELECT otp, expires_at FROM otp_verification WHERE username=?",
            (username,)
        )
        row = cursor.fetchone()

        if not row:
            return "Invalid request"

        otp, expires_at = row

        if time.time() > expires_at:
            return "OTP expired"

        if entered_otp == otp:
            cursor.execute("DELETE FROM otp_verification WHERE username=?", (username,))
            cursor.execute("UPDATE users SET verified=1 WHERE username=?", (username,))
            conn.commit()
            return redirect("/login")

        return "Invalid OTP"

    return render_template("verify.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT verified FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()

        if not user:
            return "Invalid credentials"

        if user[0] == 0:
            return "Please verify your account first"

        session["user"] = username
        return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html", user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
