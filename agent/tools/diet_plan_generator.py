def generate_diet_plan(
    goal: str,
    height_cm: float,
    weight_kg: float,
    age: int,
    gender: str,
    dietary_preference: str,
    allergies: list[str],
    calorie_target: int = None
) -> dict:
    """
    Calculates BMR and TDEE using Mifflin-St Jeor formula, returns plan skeleton.
    LLM fills actual Indian dish names based on preference and allergies.
    """
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    tdee = bmr * 1.55  # moderate activity

    if goal == "lose_weight":
        target = int(tdee - 500)
    elif goal == "gain_weight":
        target = int(tdee + 400)
    else:
        target = int(tdee)

    bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)

    return {
        "goal": goal,
        "calorie_target": calorie_target or target,
        "bmi": bmi,
        "dietary_preference": dietary_preference,
        "allergies": allergies,
        "meal_slots": []  # LLM populates with 5 real Indian meal slots
    }
