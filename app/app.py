from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "devops-production-secret"

# In-memory storage (DB comes later in real prod)
USERS = {}
ENROLLMENTS = {}

COURSES = [
    "Linux Fundamentals",
    "Git & GitHub",
    "Docker & Containers",
    "CI/CD with Jenkins",
    "Kubernetes (K8s)",
    "AWS for DevOps",
]

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USERS:
            return render_template("register.html", error="User already exists")

        USERS[username] = password
        ENROLLMENTS[username] = []
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if USERS.get(username) == password:
            session["user"] = username
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user = session["user"]

    if request.method == "POST":
        course = request.form["course"]
        if course not in ENROLLMENTS[user]:
            ENROLLMENTS[user].append(course)

    return render_template(
        "dashboard.html",
        user=user,
        courses=COURSES,
        enrolled=ENROLLMENTS[user]
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
