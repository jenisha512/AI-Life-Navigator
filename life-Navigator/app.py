from flask import Flask, jsonify, render_template, request

from config import Config
from rapidfuzz import process
from services.allocation_engine import rank_hospitals
from services.chatbot_service import generate_chatbot_reply
from utils.data_loader import load_hospitals


app = Flask(__name__)
app.config.from_object(Config)


def build_dataset_snapshot(df):
    if df is None or df.empty:
        return {
            "total_hospitals": 0,
            "total_states": 0,
            "total_cities": 0,
            "total_icu_beds": 0,
            "cardiac_ready": 0,
            "trauma_ready": 0,
            "burn_ready": 0,
            "tertiary_centers": 0,
            "last_updated": "Unknown"
        }

    yes_count = (
        lambda column: int(df[column].fillna("No").eq("Yes").sum())
        if column in df.columns
        else 0
    )
    last_updated = "Unknown"
    if "last_updated" in df.columns:
        valid_updates = df["last_updated"].dropna()
        if not valid_updates.empty:
            last_updated = str(valid_updates.max())

    return {
        "total_hospitals": int(len(df)),
        "total_states": int(df["state"].dropna().nunique()) if "state" in df.columns else 0,
        "total_cities": int(df["city"].dropna().nunique()) if "city" in df.columns else 0,
        "total_icu_beds": int(df["icu_beds"].fillna(0).sum()) if "icu_beds" in df.columns else 0,
        "cardiac_ready": yes_count("cardiac_unit"),
        "trauma_ready": yes_count("trauma_unit"),
        "burn_ready": yes_count("burn_unit"),
        "tertiary_centers": (
            int(df["hospital_level"].fillna("").eq("Tertiary").sum())
            if "hospital_level" in df.columns
            else 0
        ),
        "last_updated": last_updated
    }


try:
    hospitals_df = load_hospitals(Config.DATASET_PATH)
    hospitals_df["city"] = hospitals_df["city"].str.lower().str.strip()
    print("Hospital dataset loaded:", hospitals_df.shape)
except Exception as exc:
    print("Failed to load hospital dataset:", exc)
    hospitals_df = None

dataset_snapshot = build_dataset_snapshot(hospitals_df)


def get_best_city_match(user_city, available_cities, threshold=70):
    match = process.extractOne(
        user_city,
        available_cities,
        score_cutoff=threshold
    )
    return match[0] if match else None


@app.route("/")
def index():
    return render_template("index.html", dataset_snapshot=dataset_snapshot)


@app.route("/cities")
def cities():
    if hospitals_df is None:
        return jsonify([])

    query = request.args.get("q", "").strip().lower()
    if len(query) < 2:
        return jsonify([])

    city_list = hospitals_df["city"].unique().tolist()
    matches = [city for city in city_list if query in city]
    return jsonify(sorted(matches)[:10])


@app.route("/states")
def states():
    if hospitals_df is None:
        return jsonify([])

    return jsonify(sorted(hospitals_df["state"].dropna().unique().tolist()))


@app.route("/cities_by_state")
def cities_by_state():
    if hospitals_df is None:
        return jsonify([])

    state = request.args.get("state", "").strip().lower()
    if not state:
        return jsonify([])

    cities_in_state = (
        hospitals_df[hospitals_df["state"].str.lower() == state]["city"]
        .dropna()
        .unique()
        .tolist()
    )
    return jsonify(sorted(cities_in_state))


@app.route("/allocate", methods=["POST"])
def allocate():
    if hospitals_df is None:
        return render_template(
            "result.html",
            hospitals=[],
            emergency=None,
            severity="Low",
            error="Hospital dataset not available.",
            selected_city=None
        )

    raw_city = request.form.get("city", "").strip().lower()
    emergency = request.form.get("emergency", "General").strip()
    severity_input = request.form.get("severity", "1")

    if not raw_city:
        return render_template(
            "result.html",
            hospitals=[],
            emergency=emergency,
            severity="Low",
            error="Enter a city to continue.",
            selected_city=None
        )

    try:
        severity_score = int(severity_input)
    except ValueError:
        severity_score = 1

    if severity_score >= 4:
        severity_label = "High"
    elif severity_score >= 2:
        severity_label = "Moderate"
    else:
        severity_label = "Low"

    available_cities = hospitals_df["city"].unique().tolist()

    if raw_city not in available_cities:
        corrected_city = get_best_city_match(raw_city, available_cities)
        if corrected_city:
            city = corrected_city
        else:
            return render_template(
                "result.html",
                hospitals=[],
                emergency=emergency,
                severity=severity_label,
                error=f"No matching city found for '{raw_city}'.",
                selected_city=raw_city.title()
            )
    else:
        city = raw_city

    city_hospitals = hospitals_df[hospitals_df["city"] == city]

    if city_hospitals.empty:
        return render_template(
            "result.html",
            hospitals=[],
            emergency=emergency,
            severity=severity_label,
            error=f"No hospitals available in {city.title()}.",
            selected_city=city.title()
        )

    ranked = rank_hospitals(city_hospitals, severity_score, emergency)

    if ranked.empty:
        return render_template(
            "result.html",
            hospitals=[],
            emergency=emergency,
            severity=severity_label,
            error="No suitable hospitals found for this condition.",
            selected_city=city.title()
        )

    return render_template(
        "result.html",
        hospitals=ranked.to_dict(orient="records"),
        emergency=emergency,
        severity=severity_label,
        error=None,
        selected_city=city.title()
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a question to continue."})

    context = {}
    try:
        if hospitals_df is not None and len(hospitals_df) > 0:
            context = {
                "hospital_name": request.args.get("hospital"),
                "icu_load": request.args.get("icu_load"),
                "icu_beds": request.args.get("icu_beds"),
                "severity": request.args.get("severity"),
                "emergency": request.args.get("emergency"),
                "hospital_level": request.args.get("hospital_level"),
                "score": request.args.get("score"),
                "city": request.args.get("city"),
                "confidence": request.args.get("confidence"),
                "reason": request.args.get("reason")
            }
    except Exception:
        pass

    reply = generate_chatbot_reply(user_message, context)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
