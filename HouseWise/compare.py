
# ── Scoring weights (must sum to 1.0) ────────────────────────────────────────
WEIGHTS = {
    "advertised_rent":        0.10,
    "true_monthly_cost":      0.20,
    "bills_included":         0.10,
    "deposit":                0.10,
    "distance_from_campus":   0.10,
    "transport":              0.10,
    "area_safety":            0.15,
    "student_reviews":        0.10,
    "transparency_score":     0.05,
}

# ── Input helpers ─────────────────────────────────────────────────────────────

def prompt_float(label, unit=""):
    suffix = f" ({unit})" if unit else ""
    while True:
        raw = input(f"    {label}{suffix}: ").strip()
        try:
            val = float(raw)
            if val < 0:
                print("    → Must be a positive number.")
            else:
                return val
        except ValueError:
            print("    → Please enter a number (e.g. 750 or 1.2).")

def prompt_int(label, lo, hi):
    while True:
        raw = input(f"    {label} ({lo}–{hi}): ").strip()
        try:
            val = int(raw)
            if lo <= val <= hi:
                return val
            print(f"    → Must be between {lo} and {hi}.")
        except ValueError:
            print("    → Please enter a whole number.")

def prompt_yes_no(label):
    while True:
        raw = input(f"    {label} (y/n): ").strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("    → Please enter y or n.")

def collect_advert(name):
    print(f"\n  {'─'*50}")
    print(f"  Advert {name}")
    print(f"  {'─'*50}")
    return {
        "name":                 name,
        "advertised_rent":      prompt_float("Advertised rent", "£/month"),
        "true_monthly_cost":    prompt_float("True monthly cost (all extras included)", "£/month"),
        "bills_included":       prompt_yes_no("Bills included?"),
        "deposit":              prompt_float("Deposit", "£"),
        "distance_km":          prompt_float("Distance from campus", "km"),
        "transport_score":      prompt_int("Transport score", 1, 10),
        "area_safety_score":    prompt_int("Area safety score", 1, 10),
        "student_review_score": prompt_int("Student review score", 1, 10),
        "transparency_score":   prompt_int("Overall Transparency Score", 0, 100),
    }

# ── Scoring ───────────────────────────────────────────────────────────────────

def norm_lower(value, a_val, b_val):
    """Lower is better — returns 0–10."""
    lo, hi = min(a_val, b_val), max(a_val, b_val)
    if hi == lo:
        return 10.0
    return 10.0 * (1.0 - (value - lo) / (hi - lo))

def score_advert(advert, other):
    s = {}
    s["advertised_rent"]      = norm_lower(advert["advertised_rent"],   advert["advertised_rent"],   other["advertised_rent"])
    s["true_monthly_cost"]    = norm_lower(advert["true_monthly_cost"], advert["true_monthly_cost"], other["true_monthly_cost"])
    s["deposit"]              = norm_lower(advert["deposit"],           advert["deposit"],           other["deposit"])
    s["distance_from_campus"] = norm_lower(advert["distance_km"],       advert["distance_km"],       other["distance_km"])
    s["bills_included"]       = 10.0 if advert["bills_included"] else 0.0
    s["transport"]            = float(advert["transport_score"])
    s["area_safety"]          = float(advert["area_safety_score"])
    s["student_reviews"]      = float(advert["student_review_score"])
    s["transparency_score"]   = advert["transparency_score"] / 10.0
    total = sum(s[k] * WEIGHTS[k] for k in WEIGHTS) * 10
    return {"components": s, "total": round(total, 1)}

# ── Recommendation logic (no AI — pure rule-based) ────────────────────────────

COMPONENT_LABELS = {
    "advertised_rent":      "lower advertised rent",
    "true_monthly_cost":    "lower true monthly cost",
    "bills_included":       "bills being included",
    "deposit":              "a smaller deposit",
    "distance_from_campus": "being closer to campus",
    "transport":            "better transport links",
    "area_safety":          "a safer area",
    "student_reviews":      "stronger student reviews",
    "transparency_score":   "a higher transparency score",
}

DISPLAY_LABELS = {
    "advertised_rent":      "Advertised rent",
    "true_monthly_cost":    "True monthly cost",
    "bills_included":       "Bills included",
    "deposit":              "Deposit",
    "distance_from_campus": "Distance from campus",
    "transport":            "Transport",
    "area_safety":          "Area safety",
    "student_reviews":      "Student reviews",
    "transparency_score":   "Transparency score",
}

def build_recommendation(advert_a, advert_b, scores_a, scores_b):
    sa, sb = scores_a["total"], scores_b["total"]
    winner = "A" if sa >= sb else "B"
    w_scores = scores_a if winner == "A" else scores_b
    l_scores  = scores_b if winner == "A" else scores_a
    w_advert  = advert_a if winner == "A" else advert_b
    l_advert  = advert_b if winner == "A" else advert_a
    loser     = "B" if winner == "A" else "A"

    diff = abs(sa - sb)
    if diff < 3:
        verdict = "a close call, but edges ahead"
    elif diff < 10:
        verdict = "the better choice"
    else:
        verdict = "clearly the stronger option"

    advantages = {k: w_scores["components"][k] - l_scores["components"][k] for k in WEIGHTS}
    best_key  = max(advantages, key=advantages.get)
    weaknesses = {k: l_scores["components"][k] - w_scores["components"][k] for k in WEIGHTS}
    worst_key = min(weaknesses, key=weaknesses.get)

    lines = [
        f"Advert {winner} is {verdict} with a weighted score of "
        f"{sa if winner == 'A' else sb:.1f} vs {sb if winner == 'A' else sa:.1f}/100.",

        f"Its biggest advantage is {COMPONENT_LABELS[best_key]}, "
        f"which has a meaningful impact on day-to-day student life.",

        f"Advert {loser} is weakest on {COMPONENT_LABELS[worst_key]}, "
        f"which pulls its overall score down.",
    ]

    if w_advert["bills_included"] and not l_advert["bills_included"]:
        lines.append(
            f"Bills are included in Advert {winner}, making monthly budgeting "
            f"much simpler — no surprise utility bills mid-term."
        )
    elif not w_advert["bills_included"] and l_advert["bills_included"]:
        lines.append(
            f"Note: Advert {winner} does not include bills. Add ~£80–120/month "
            f"to your true cost estimate."
        )

    lines.append(f"Recommendation: go with Advert {winner}.")
    return " ".join(lines)

# ── Report printer ────────────────────────────────────────────────────────────

def wrap_text(text, width=60, indent="  "):
    words = text.split()
    lines, line = [], indent
    for word in words:
        if len(line) + len(word) + 1 > width:
            lines.append(line.rstrip())
            line = indent + word + " "
        else:
            line += word + " "
    if line.strip():
        lines.append(line.rstrip())
    return "\n".join(lines)

def print_report(advert_a, advert_b, scores_a, scores_b, recommendation):
    winner = "A" if scores_a["total"] >= scores_b["total"] else "B"
    W = 60

    def row(label, val_a, val_b):
        print(f"  {label:<26} {str(val_a):<16} {val_b}")

    print(f"\n  {'═'*W}")
    print(f"  {'HOUSEWISE — PROPERTY COMPARISON':^{W}}")
    print(f"  {'═'*W}")

    print(f"\n  {'INPUT DATA':<26} {'Advert A':<16} Advert B")
    print(f"  {'─'*W}")
    row("Advertised rent",        f"£{advert_a['advertised_rent']:.0f}/mo",     f"£{advert_b['advertised_rent']:.0f}/mo")
    row("True monthly cost",      f"£{advert_a['true_monthly_cost']:.0f}/mo",   f"£{advert_b['true_monthly_cost']:.0f}/mo")
    row("Bills included",         "Yes" if advert_a["bills_included"] else "No", "Yes" if advert_b["bills_included"] else "No")
    row("Deposit",                f"£{advert_a['deposit']:.0f}",                f"£{advert_b['deposit']:.0f}")
    row("Distance from campus",   f"{advert_a['distance_km']:.1f} km",          f"{advert_b['distance_km']:.1f} km")
    row("Transport (1–10)",       advert_a["transport_score"],                   advert_b["transport_score"])
    row("Area safety (1–10)",     advert_a["area_safety_score"],                 advert_b["area_safety_score"])
    row("Student reviews (1–10)", advert_a["student_review_score"],              advert_b["student_review_score"])
    row("Transparency score",     f"{advert_a['transparency_score']}/100",       f"{advert_b['transparency_score']}/100")

    print(f"\n  {'COMPONENT SCORES (0–10)':<26} {'Advert A':<16} Advert B")
    print(f"  {'─'*W}")
    for key, label in DISPLAY_LABELS.items():
        sa = scores_a["components"][key]
        sb = scores_b["components"][key]
        mark_a = " ◀" if sa > sb else ""
        mark_b = " ◀" if sb > sa else ""
        print(f"  {label:<26} {sa:>5.1f}{mark_a:<11} {sb:>5.1f}{mark_b}")

    print(f"  {'─'*W}")
    print(f"  {'WEIGHTED TOTAL':<26} {scores_a['total']:>5.1f}{'':11} {scores_b['total']:>5.1f}")

    print(f"\n  {'─'*W}")
    print(f"  RECOMMENDATION")
    print(f"  {'─'*W}")
    print(wrap_text(recommendation, width=62, indent="  "))

    print(f"\n  {'═'*W}")
    print(f"  {'★  RECOMMENDED: ADVERT ' + winner + '  ★':^{W}}")
    print(f"  {'═'*W}\n")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n  Score guide:")
    print("  Transport / safety / reviews → 1 (poor) to 10 (excellent)")
    print("  Transparency score           → 0 to 100\n")

    advert_a = collect_advert("A")
    advert_b = collect_advert("B")

    scores_a = score_advert(advert_a, advert_b)
    scores_b = score_advert(advert_b, advert_a)
    recommendation = build_recommendation(advert_a, advert_b, scores_a, scores_b)

    print_report(advert_a, advert_b, scores_a, scores_b, recommendation)

if __name__ == "__main__":
    main()