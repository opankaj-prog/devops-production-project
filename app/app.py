from flask import Flask, render_template, request, redirect, session, url_for
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = "devops-production-secret"

# ---- In-memory DB (replace with RDS later) ----
USERS = {}
OTP_STORE = {}
COURSES = {
    "Docker": ["What is Docker?", "Docker Images", "Docker Containers"],
    "Kubernetes": ["K8s Basics", "Pods", "Services"]
}
ENROLLMENTS = {}
PROGRESS = {}

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return redirect("/login")

# ---------- AUTH ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        email = request.form["email"]
        mobile = request.form["mobile"]

        if user in USERS:
            return "User already exists"

        USERS[user] = {
            "password": pwd,
            "verified": False,
            "email": email,
            "mobile": mobile
        }

        otp = str(random.randint(100000, 999999))
        OTP_STORE[user] = otp
        print(f"OTP for {user}: {otp}")  # Simulated SMS/Email

        return redirect(f"/verify/{user}")

    return render_template("register.html")


@app.route("/verify/<user>", methods=["GET", "POST"])
def verify(user):
    if request.method == "POST":
        if request.form["otp"] == OTP_STORE.get(user):
            USERS[user]["verified"] = True
            ENROLLMENTS[user] = []
            PROGRESS[user] = {}
            return redirect("/login")
        return "Invalid OTP"

    return render_template("verify.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        if user == ADMIN_USER and pwd == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")

        if user in USERS and USERS[user]["password"] == pwd:
            if not USERS[user]["verified"]:
                return "Verify account first"
            session["user"] = user
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- USER ----------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]

    if request.method == "POST":
        course = request.form["course"]
        if course not in ENROLLMENTS[user]:
            ENROLLMENTS[user].append(course)
            PROGRESS[user][course] = 0

    return render_template(
        "dashboard.html",
        courses=COURSES.keys(),
        enrolled=ENROLLMENTS[user]
    )


@app.route("/course/<course>", methods=["GET", "POST"])
def course(course):
    user = session["user"]
    lessons = COURSES.get(course, [])

    if request.method == "POST":
        PROGRESS[user][course] += int(100 / len(lessons))

    return render_template(
        "course.html",
        course=course,
        lessons=lessons,
        progress=PROGRESS[user][course]
    )

# ---------- ADMIN ----------

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        cname = request.form["course"]
        lesson = request.form["lesson"]

        COURSES.setdefault(cname, []).append(lesson)

    return render_template("admin.html", courses=COURSES)


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
