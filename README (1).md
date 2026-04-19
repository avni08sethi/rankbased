# ACO-TSP Visualizer — Full-Stack Project

An interactive full-stack web app for visualizing **Ant Colony Optimization** solving the **Traveling Salesman Problem**.

## Project Structure

```
aco_tsp/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── requirements.txt
│   ├── routes/
│   │   ├── __init__.py
│   │   └── optimize.py         # POST /optimize endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   └── aco.py              # All 3 ACO algorithms + factory
│   └── models/
│       ├── __init__.py
│       └── schemas.py          # Data shapes / documentation
├── frontend/
│   └── index.html              # Single-file React-free frontend
└── README.md
```

## Features

| Feature | Details |
|---|---|
| **3 ACO Algorithms** | Ant System · Elitist AS · Rank-Based AS |
| **Comparison mode** | Run all 3 side-by-side, highlights the winner |
| **Animated path** | Edge-by-edge tour animation with color coding |
| **Convergence chart** | Best-distance-per-iteration line chart |
| **Random city gen** | Instant random coordinate generation |
| **Manual input** | Paste x,y coordinates manually |
| **Tunable params** | Iterations (10–500), Ants (2–100) |
| **Live API status** | Shows backend connection health in header |

---

## 1 — Backend Setup

### Prerequisites
- Python 3.9+
- pip

### Install & Run

```bash
# 1. Navigate to backend
cd aco_tsp/backend

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask server
python app.py
```

The API starts at **http://localhost:5000**

---

## 2 — Frontend Setup

The frontend is a **single HTML file** — no Node.js, no build step needed.

### Option A: Direct open (simplest)
```bash
# Just open in your browser
open aco_tsp/frontend/index.html        # Mac
start aco_tsp/frontend/index.html       # Windows
xdg-open aco_tsp/frontend/index.html   # Linux
```

### Option B: Serve with Python (avoids any CORS edge cases)
```bash
cd aco_tsp/frontend
python -m http.server 3000
# Open http://localhost:3000
```

### Option C: Serve with Node (if you have it)
```bash
npx serve aco_tsp/frontend
```

---

## 3 — Usage

1. Open the frontend in your browser
2. Make sure the **API endpoint** in the sidebar matches your Flask server URL (default: `http://localhost:5000`)
3. The status dot turns **green** when the backend is reachable
4. **Generate random cities** or type coordinates manually (one `x, y` per line)
5. Choose an algorithm (or "Compare all")
6. Click **Run Optimization**
7. Watch the animated tour appear; switch to **Convergence** tab to see iteration history

---

## 4 — API Reference

### `GET /`
Health check.

**Response:**
```json
{ "status": "ok", "message": "ACO-TSP API is running" }
```

---

### `POST /optimize`

**Request body:**
```json
{
  "coords":     [[20.5, 34.1], [80.2, 12.9], [55.0, 70.3]],
  "algorithm":  "ant_system",
  "iterations": 50,
  "n_ants":     10
}
```

| Field | Type | Default | Options |
|---|---|---|---|
| `coords` | `[[float, float]]` | required | ≥ 3 cities |
| `algorithm` | `string` | `"ant_system"` | `"ant_system"` · `"elitist"` · `"rank_based"` · `"all"` |
| `iterations` | `int` | `50` | 1–500 |
| `n_ants` | `int` | `10` | 2–100 |

**Response:**
```json
{
  "results": [
    {
      "algorithm":     "ant_system",
      "best_path":     [0, 4, 2, 7, 1, 3, 5, 6],
      "best_distance": 312.45,
      "exec_time":     0.08,
      "convergence":   [450.2, 380.1, 330.5, ...]
    }
  ],
  "coords": [[20.5, 34.1], ...]
}
```

---

## 5 — Algorithm Details

### Ant System (Dorigo, 1992)
All ants deposit pheromone each iteration proportional to `Q / distance`. Evaporation applied before deposit.

### Elitist Ant System
Same as AS, but the **best-so-far** solution gets extra pheromone reinforcement with multiplier `e=5` on top of normal deposits.

### Rank-Based Ant System (AS_rank)
Only the **top-w ants** by tour quality deposit pheromone, weighted linearly by rank (`w`, `w-1`, ..., `1`). Best-so-far ant also contributes with weight `w`.

---

## 6 — Deployment

### Backend — Render.com

1. Push the `backend/` folder to a GitHub repo
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your repo
4. Set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
5. Add env var: `PYTHON_VERSION = 3.11.0`

Install gunicorn first:
```bash
pip install gunicorn
echo "gunicorn" >> requirements.txt
```

### Frontend — Vercel / Netlify

Since the frontend is a single HTML file, you can:

**Vercel:**
```bash
npx vercel aco_tsp/frontend
```

**Netlify:**
Drag and drop the `frontend/` folder at [app.netlify.com/drop](https://app.netlify.com/drop)

> After deploying the backend, update the API endpoint URL in the frontend's sidebar input to point to your Render URL (e.g., `https://aco-tsp.onrender.com`).

---

## 7 — Extending the Project

### Add a new algorithm
1. Create a new class in `backend/services/aco.py` extending `AntColonyBase`
2. Override the `optimize()` method
3. Add it to the `ALGORITHM_MAP` dict at the bottom of `aco.py`
4. Add its color and label in the frontend's `COLORS` and `LABELS` objects

### Add a React frontend
The backend is fully CORS-enabled. To use React:
```bash
npx create-react-app frontend
cd frontend
npm install axios
```
Use `axios.post('http://localhost:5000/optimize', payload)` to connect.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| flask | 3.0.3 | Web framework |
| flask-cors | 4.0.1 | Cross-origin resource sharing |
| numpy | 1.26.4 | Matrix math for distance/pheromone |
| Chart.js | 4.4.1 | Convergence chart (CDN) |
