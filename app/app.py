from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Your MLOps Production App is running..., healthy..., and secure. your app is reached to end users and accessible from anywhere across the world "

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
