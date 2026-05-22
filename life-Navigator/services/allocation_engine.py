def to_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def get_icu_availability_points(hospital):
    icu_beds = to_int(hospital.get("icu_beds", 0))
    if icu_beds <= 0:
        return 0
    return min(30, 18 + (icu_beds // 4))


def get_specialization_points(hospital, emergency_type):
    if emergency_type == "Cardiac" and hospital.get("cardiac_unit") == "Yes":
        return 24

    if emergency_type == "Trauma" and hospital.get("trauma_unit") == "Yes":
        return 24

    if emergency_type == "Burn" and hospital.get("burn_unit") == "Yes":
        return 24

    if emergency_type == "General":
        return 12

    return 0


def get_load_points(hospital):
    load_percent = to_int(hospital.get("current_icu_load_percent", 100), 100)
    if load_percent < 35:
        return 20
    if load_percent < 50:
        return 17
    if load_percent < 65:
        return 14
    if load_percent < 80:
        return 8
    if load_percent < 90:
        return 0
    return -8


def get_severity_points(severity):
    return severity * 3


def get_capability_points(hospital, severity):
    hospital_level = str(hospital.get("hospital_level", "")).strip().lower()
    if hospital_level == "tertiary":
        return 10 if severity >= 4 else 7
    if hospital_level == "secondary":
        return 6 if severity >= 4 else 4
    if hospital_level == "primary":
        return 3
    return 0


def describe_load_band(load_percent):
    if load_percent < 50:
        return "Low ICU pressure"
    if load_percent < 75:
        return "Balanced ICU pressure"
    return "High ICU pressure"


def get_specialty_label(hospital, emergency_type):
    if emergency_type == "Cardiac":
        return "Cardiac support confirmed" if hospital.get("cardiac_unit") == "Yes" else "Cardiac support not confirmed"

    if emergency_type == "Trauma":
        return "Trauma support confirmed" if hospital.get("trauma_unit") == "Yes" else "Trauma support not confirmed"

    if emergency_type == "Burn":
        return "Burn support confirmed" if hospital.get("burn_unit") == "Yes" else "Burn support not confirmed"

    return "General emergency intake"


def build_confidence_label(availability_points, specialization_points, load_points, capability_points):
    if availability_points >= 24 and specialization_points >= 24 and load_points >= 8 and capability_points >= 6:
        return "High confidence"
    if availability_points >= 18 and load_points >= 8:
        return "Operationally strong"
    return "Use shortlist review"


def build_recommendation_reason(
    hospital,
    emergency_type,
    availability_points,
    specialization_points,
    load_points,
    capability_points
):
    reasons = []

    if availability_points:
        reasons.append("ICU capacity is available")
    else:
        reasons.append("ICU capacity is limited")

    if emergency_type != "General":
        reasons.append(
            "specialty support is aligned"
            if specialization_points >= 24
            else "specialty fit is weaker than ideal"
        )
    else:
        reasons.append("general emergency intake is supported")

    reasons.append(
        "operational load is manageable"
        if load_points > 0
        else "operational load is relatively high"
    )

    if capability_points >= 10:
        reasons.append("tertiary-level capability strengthens escalation readiness")
    elif capability_points >= 6:
        reasons.append("care level is well suited to urgent stabilization")

    first_reason = reasons[0]
    remaining_reasons = ", ".join(reasons[1:])
    return f"{first_reason}, {remaining_reasons}." if remaining_reasons else f"{first_reason}."


def score_hospital(hospital, severity, emergency_type):
    availability_points = get_icu_availability_points(hospital)
    specialization_points = get_specialization_points(hospital, emergency_type)
    load_points = get_load_points(hospital)
    severity_points = get_severity_points(severity)
    capability_points = get_capability_points(hospital, severity)

    score = (
        availability_points
        + specialization_points
        + load_points
        + severity_points
        + capability_points
    )

    return {
        "score": score,
        "availability_points": availability_points,
        "specialization_points": specialization_points,
        "load_points": load_points,
        "severity_points": severity_points,
        "capability_points": capability_points,
        "load_band": describe_load_band(hospital.get("current_icu_load_percent", 100)),
        "specialty_label": get_specialty_label(hospital, emergency_type),
        "confidence_label": build_confidence_label(
            availability_points,
            specialization_points,
            load_points,
            capability_points
        ),
        "recommendation_reason": build_recommendation_reason(
            hospital,
            emergency_type,
            availability_points,
            specialization_points,
            load_points,
            capability_points
        )
    }


def rank_hospitals(df, severity, emergency_type, top_n=5):
    if df.empty:
        return df

    df = df.copy()

    score_details = df.apply(
        lambda row: score_hospital(row, severity, emergency_type),
        axis=1,
        result_type="expand"
    )
    df = df.join(score_details)

    return df.sort_values(
        by=["score", "current_icu_load_percent", "icu_beds"],
        ascending=[False, True, False]
    ).head(top_n)
