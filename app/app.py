from flask import Flask, jsonify, request
import socket
import time
import threading

app = Flask(__name__)

# ---- Runtime State (real activity) ----
START_TIME = time.time()
REQUEST_COUNT = 0
LAST_REQUEST_TIME = None
HOSTNAME = socket.gethostname()

# Background activity (simulates real service behavior)
def background_worker():
    while True:
        time.sleep(10)

threading.Thread(target=background_worker, daemon=True).start()


@app.before_request
def track_requests():
    global REQUEST_COUNT, LAST_REQUEST_TIME
    REQUEST_COUNT += 1
    LAST_REQUEST_TIME = time.strftime("%Y-%m-%d %H:%M:%S")


@app.route("/")
def home():
    uptime = int(time.time() - START_TIME)
    return f"""
    <h2>🚀 Production Application</h2>
    <p><b>Container Name:</b> {HOSTNAME}</p>
    <p><b>Requests Served:</b> {REQUEST_COUNT}</p>
    <p><b>Uptime:</b> {uptime} seconds</p>
    <p><b>Last Request:</b> {LAST_REQUEST_TIME}</p>
    <p><b>Client IP:</b> {request.remote_addr}</p>
    """


@app.route("/health")
def health():
    return "OK", 200


@app.route("/metrics")
def metrics():
    return jsonify({
        "container": HOSTNAME,
        "requests": REQUEST_COUNT,
        "uptime_seconds": int(time.time() - START_TIME),
        "last_request": LAST_REQUEST_TIME
    })


@app.route("/api/work")
def do_work():
    time.sleep(0.3)  # simulate processing
    return jsonify({
        "status": "processed",
        "processed_at": time.time(),
        "container": HOSTNAME
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

