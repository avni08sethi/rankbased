"""
routes/optimize.py
REST endpoint: POST /optimize
"""

from flask import Blueprint, request, jsonify
from services.aco import run_algorithm, ALGORITHM_MAP

optimize_bp = Blueprint("optimize", __name__)


@optimize_bp.route("/optimize", methods=["POST"])
def optimize():
    """
    POST /optimize
    Body (JSON):
      {
        "coords":     [[x, y], ...],   // list of city coordinates
        "algorithm":  "ant_system" | "elitist" | "rank_based" | "all",
        "iterations": 50,              // optional, default 50
        "n_ants":     10               // optional, default 10
      }

    Response (JSON):
      {
        "results": [
          {
            "algorithm":    "ant_system",
            "best_path":    [0, 3, 1, ...],
            "best_distance": 312.4,
            "exec_time":    0.08,
            "convergence":  [450.2, 380.1, ...]
          },
          ...
        ],
        "coords": [[x, y], ...]
      }
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # ── Validate coords ──────────────────────────────────────────────────────
    coords = data.get("coords")
    if not coords or not isinstance(coords, list) or len(coords) < 3:
        return jsonify({"error": "Provide at least 3 cities in 'coords'"}), 400

    for pt in coords:
        if not (isinstance(pt, (list, tuple)) and len(pt) == 2):
            return jsonify({"error": "Each coord must be [x, y]"}), 400

    # ── Parameters ───────────────────────────────────────────────────────────
    algorithm  = data.get("algorithm", "ant_system")
    iterations = int(data.get("iterations", 50))
    n_ants     = int(data.get("n_ants", 10))

    valid_algos = list(ALGORITHM_MAP.keys()) + ["all"]
    if algorithm not in valid_algos:
        return jsonify({"error": f"algorithm must be one of {valid_algos}"}), 400

    if iterations < 1 or iterations > 500:
        return jsonify({"error": "iterations must be between 1 and 500"}), 400

    if n_ants < 2 or n_ants > 100:
        return jsonify({"error": "n_ants must be between 2 and 100"}), 400

    # ── Run ──────────────────────────────────────────────────────────────────
    algo_names = list(ALGORITHM_MAP.keys()) if algorithm == "all" else [algorithm]
    results = []

    for name in algo_names:
        try:
            best_path, best_distance, exec_time, convergence = run_algorithm(
                name, coords, n_ants=n_ants, iterations=iterations
            )
            results.append({
                "algorithm":     name,
                "best_path":     best_path,
                "best_distance": round(best_distance, 4),
                "exec_time":     round(exec_time, 4),
                "convergence":   [round(v, 4) for v in convergence],
            })
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return jsonify({"results": results, "coords": coords}), 200
