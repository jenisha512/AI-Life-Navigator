def generate_chatbot_reply(message, context=None):
    """
    Context-aware medical guidance chatbot.
    Safe, deterministic, and suitable for healthcare demos.
    """

    msg = message.lower().strip()
    ctx = context or {}

    hospital = ctx.get("hospital_name", "the recommended hospital")
    icu_load = ctx.get("icu_load")
    icu_beds = ctx.get("icu_beds")
    severity = ctx.get("severity", "the assessed level")
    emergency = ctx.get("emergency", "your condition")
    hospital_level = ctx.get("hospital_level", "the listed care level")
    score = ctx.get("score")
    city = ctx.get("city", "the selected area")
    confidence = ctx.get("confidence", "the current confidence band")
    reason = ctx.get("reason")

    # --- WHY THIS HOSPITAL ---
    if any(k in msg for k in ["why", "recommended", "selected", "best hospital", "top hospital"]):
        return (
            f"{hospital} ranked first for the {emergency.lower()} case in {city} because it combines "
            f"{hospital_level.lower()} capability with manageable ICU pressure"
            f"{f' ({icu_load}% occupied)' if icu_load is not None else ''}"
            f"{f' and a score of {score}' if score else ''}. "
            f"{reason + ' ' if reason else ''}"
            "In short, it balances specialty fit, available capacity, and response readiness better than the other options."
        )

    # --- ICU EXPLANATION ---
    if any(k in msg for k in ["icu", "bed", "capacity", "load"]):
        load_summary = (
            f"with a current ICU load of {icu_load}%."
            if icu_load is not None
            else "with adequate capacity in the dataset."
        )
        return (
            f"ICU load indicates how many ICU beds are currently occupied. "
            f"{hospital} has "
            f"{f'{icu_beds} ICU beds available' if icu_beds else 'adequate ICU capacity'}, "
            f"{load_summary}"
        )

    # --- SEVERITY ---
    if any(k in msg for k in ["severity", "serious", "risk"]):
        return (
            f"The severity level is assessed as {severity}. "
            "This helps prioritize hospitals that can provide the required level of care "
            "without unnecessary delay."
        )

    # --- RANKING SCORE ---
    if any(k in msg for k in ["score", "ranking", "rank"]):
        return (
            f"The ranking score is a composite signal, not a diagnosis. "
            f"For {hospital}, the score reflects ICU readiness, emergency specialization, and current operational load"
            f"{f' and reached {score}' if score else ''}. "
            "Higher scores mean the hospital is a stronger operational match for this case."
        )

    if any(k in msg for k in ["confidence", "strong match", "how good", "fit", "match"]):
        return (
            f"The recommendation is currently tagged as {confidence.lower()}. "
            "That label is based on whether the hospital has ICU capacity, the right emergency support signal, and a manageable ICU load."
        )

    # --- ALTERNATIVES ---
    if any(k in msg for k in ["alternative", "backup", "another hospital"]):
        return (
            "The ranked list should be treated as a shortlist, not a single forced choice. "
            "If travel conditions change or the top facility becomes unavailable, use the next-ranked hospitals as backup options."
        )

    # --- DIRECTIONS ---
    if any(k in msg for k in ["direction", "route", "map", "travel"]):
        return (
            "Use the directions button on the page to open the selected hospital in Google Maps. "
            "That is the quickest way to move from a recommendation to route planning."
        )

    # --- WHAT SHOULD I DO NOW ---
    if any(k in msg for k in ["what next", "what should i do", "next step", "now what"]):
        return (
            "Please proceed to the recommended hospital as soon as possible. "
            "Carry previous medical reports, current medications, and ensure "
            "someone accompanies the patient if possible."
        )

    # --- TRUST / EXPLAINABILITY ---
    if any(k in msg for k in ["trust", "reliable", "confidence", "explainable"]):
        return (
            "This system is designed as decision support, not a replacement for clinical judgment. "
            "Its value is that the hospital choice can be explained using visible factors like ICU load, specialty support, and care level."
        )

    # --- EMERGENCY SAFETY ---
    if any(k in msg for k in ["emergency", "urgent", "critical"]):
        return (
            "If symptoms worsen or the patient becomes unresponsive, "
            "seek emergency medical care immediately or call local emergency services."
        )

    # --- FALLBACK ---
    return (
        f"I can explain why {hospital} ranked first, what the ICU load means, how the severity level affects the shortlist, "
        "and what next steps make sense. Please ask your question."
    )
