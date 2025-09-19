from flask import Flask, jsonify, render_template
from utils.monitor import get_system_metrics

app = Flask(__name__)

@app.route("/metrics")
def metrics():
    """Return live system metrics as JSON."""
    return jsonify(get_system_metrics())

@app.route("/")
def home():
    """Temporary home page (frontend will come later)."""
    return "<h2>System Monitor API is running. Visit /metrics for data.</h2>"

if __name__ == "__main__":
    app.run(debug=True)
