FOODS_REQUIRING_CONTEXT = {
    "ghee": ["activity_level", "cholesterol_history"],
    "coconut oil": ["activity_level", "cholesterol_history"],
    "jaggery": ["blood_sugar_history"],
    "pickle": ["blood_pressure_history"],
    "chai": ["caffeine_sensitivity", "sleep_quality"],
    "alcohol": ["liver_history"],
    "red meat": ["cholesterol_history", "uric_acid_history"],
    "salt": ["blood_pressure_history"],
    "butter": ["cholesterol_history"],
    "paneer": ["lactose_tolerance", "cholesterol_history"],
}

def food_analyzer(
    food_name: str,
    user_profile: dict,
    additional_context: dict = None
) -> dict:
    """
    Analyzes a food item. Returns needs_context=True with required_fields
    if critical personal health context is missing, triggering INTERRUPT mode.
    """
    food_lower = food_name.lower()
    for key, required_fields in FOODS_REQUIRING_CONTEXT.items():
        if key in food_lower:
            missing = [
                f for f in required_fields
                if not (additional_context or {}).get(f)
            ]
            if missing:
                return {
                    "needs_context": True,
                    "required_fields": missing,
                    "food_name": food_name
                }

    return {
        "food_name": food_name,
        "needs_context": False,
        "calories_per_serving": None,   # LLM fills
        "macros": {},                   # LLM fills
        "benefits": [],                 # LLM fills
        "drawbacks": [],                # LLM fills
        "verdict_for_user": "",         # LLM personalises
    }
