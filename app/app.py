from flask import Flask, render_template, request
import socket
import time

app = Flask(__name__)

start_time = time.time()
request_count = 0
container_name = socket.gethostname()

@app.route("/", methods=["GET", "POST"])
def home():
    global request_count
    request_count += 1

    user_message = None
    if request.method == "POST":
        user_message = request.form.get("message")

    uptime = int(time.time() - start_time)

    return render_template(
        "index.html",
        container_name=container_name,
        requests=request_count,
        uptime=uptime,
        user_message=user_message
    )

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

