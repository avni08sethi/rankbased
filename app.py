"""
ACO-TSP Backend — Flask REST API
Entry point: runs the Flask app with CORS enabled.
"""

from flask import Flask
from flask_cors import CORS
from routes.optimize import optimize_bp

app = Flask(__name__)
CORS(app)  # Allow all origins (restrict in production)

# Register blueprints
app.register_blueprint(optimize_bp)

@app.route("/", methods=["GET"])
def health():
    return {"status": "ok", "message": "ACO-TSP API is running"}, 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
