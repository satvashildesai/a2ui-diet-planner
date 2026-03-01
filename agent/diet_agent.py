"""
Diet Agent - Core agent logic using Google ADK + Gemini 2.5 Flash
Falls back to direct Gemini API if Google ADK is not fully configured.
"""
import json
import re
import asyncio
from typing import AsyncGenerator, Optional

from schemas.session_state import SessionState, AgentMode, ConversationMessage
from tools.guardrail_checker import guardrail_checker
from tools.diet_plan_generator import generate_diet_plan
from tools.food_analyzer import food_analyzer
from tools.context_evaluator import context_evaluator
from prompts.system_prompt import SYSTEM_PROMPT

from datetime import datetime

try:
    import google.generativeai as genai
    import os
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    HAS_GEMINI = bool(GEMINI_API_KEY)
except ImportError:
    HAS_GEMINI = False


def build_session_context(session: SessionState, additional_context: dict = None) -> str:
    """Build a JSON context string from session state for the LLM."""
    ctx = {
        "mode": session.mode.value,
        "hasUserProfile": session.user_profile is not None,
        "hasActivePlan": session.active_plan is not None,
        "pendingQuestion": session.pending_question,
    }
    if session.user_profile:
        ctx["userProfile"] = session.user_profile.model_dump()
    if session.active_plan:
        ctx["activePlan"] = session.active_plan.model_dump()
    if additional_context:
        ctx["additionalContext"] = additional_context
    return json.dumps(ctx, indent=2)


def parse_agent_response(raw_response: str) -> tuple[str, list[dict]]:
    """
    Parse agent response into (conversational_text, a2ui_messages).
    Expected format:
      conversational text
      ---A2UI_JSON---
      [ ... JSON array ... ]
    """
    parts = raw_response.split("---A2UI_JSON---", 1)
    conversational_text = parts[0].strip().strip('"')

    a2ui_messages = []
    if len(parts) > 1:
        json_str = parts[1].strip()
        # Remove markdown code fences if present
        json_str = re.sub(r"^```json\s*", "", json_str)
        json_str = re.sub(r"^```\s*", "", json_str)
        json_str = re.sub(r"\s*```$", "", json_str)
        try:
            a2ui_messages = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Raw JSON: {json_str[:500]}")

    return conversational_text, a2ui_messages


def apply_tools_pre_llm(
    message: str,
    session: SessionState,
    additional_context: dict = None
) -> dict:
    """
    Apply deterministic tool logic BEFORE calling the LLM.
    Returns metadata that gets injected into the LLM prompt.
    """
    result = {}

    # 1. Guardrail check ALWAYS first
    guardrail = guardrail_checker(message)
    result["guardrail"] = guardrail

    if not guardrail["is_relevant"]:
        result["forced_mode"] = "guardrail"
        return result

    # 2. Context evaluation
    ctx_eval = context_evaluator(session.model_dump())
    result["context_eval"] = ctx_eval

    # 3. If plan_active and message looks like food analysis
    if session.mode == AgentMode.PLAN_ACTIVE and session.user_profile:
        food_keywords = [
            "ghee", "butter", "jaggery", "pickle", "chai", "tea", "salt",
            "sugar", "oil", "paneer", "red meat", "coconut", "alcohol"
        ]
        msg_lower = message.lower()
        for food in food_keywords:
            if food in msg_lower:
                food_result = food_analyzer(
                    food,
                    session.user_profile.model_dump(),
                    additional_context
                )
                result["food_analysis"] = food_result
                if food_result.get("needs_context"):
                    result["needs_interrupt"] = True
                    session.pending_question = message
                    session.mode = AgentMode.INTERRUPT_PENDING
                break

    return result


async def run_diet_agent(
    message: str,
    session: SessionState,
    additional_context: dict = None
) -> AsyncGenerator[dict, None]:
    """
    Main agent runner. Yields A2UI message chunks + metadata events.
    """
    # Update conversation history
    session.conversation_history.append(
        ConversationMessage(
            role="user",
            content=message,
            timestamp=datetime.utcnow().isoformat()
        )
    )

    # Pre-LLM tool execution
    tool_results = apply_tools_pre_llm(message, session, additional_context)

    # Build the prompt
    session_context = build_session_context(session, additional_context)
    tool_results_str = json.dumps(tool_results, indent=2)

    full_prompt = f"""
CURRENT SESSION STATE:
{session_context}

PRE-COMPUTED TOOL RESULTS (use these to inform your response):
{tool_results_str}

USER MESSAGE: {message}

Instructions:
- If forced_mode is "guardrail" in tool results → render GuardrailCard immediately
- If needs_interrupt is true → render ContextInterruptForm for the food in question
- If mode is "intake" or hasUserProfile is false → render UserProfileForm
- If mode is "plan_active" → answer the follow-up using the active plan context
- Always follow the two-part output format: conversational text, then ---A2UI_JSON---, then JSON array
"""

    # Generate response
    if HAS_GEMINI:
        response_text = await call_gemini(full_prompt)
    else:
        response_text = generate_mock_response(message, session, tool_results)

    # Parse response
    conv_text, a2ui_messages = parse_agent_response(response_text)

    # Save assistant message to history
    if conv_text:
        session.conversation_history.append(
            ConversationMessage(
                role="assistant",
                content=conv_text,
                timestamp=datetime.utcnow().isoformat()
            )
        )

    # Yield conversational text as a special chunk
    if conv_text:
        yield {"type": "text", "content": conv_text}

    # Yield A2UI messages
    for msg in a2ui_messages:
        yield msg
        await asyncio.sleep(0.01)  # Small delay for streaming effect

    # Emit mode change events
    if session.mode == AgentMode.PLAN_ACTIVE and session.active_plan:
        yield {"type": "mode_change", "mode": "plan_active"}
    elif session.mode == AgentMode.INTERRUPT_PENDING:
        yield {"type": "mode_change", "mode": "interrupt_pending"}


async def call_gemini(prompt: str) -> str:
    """Call Gemini API for agent response."""
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    response = await asyncio.to_thread(
        model.generate_content,
        prompt
    )
    return response.text


def generate_mock_response(
    message: str,
    session: SessionState,
    tool_results: dict
) -> str:
    """
    Generate a mock response when Gemini API is not available.
    Used for development/demo purposes.
    """
    msg_lower = message.lower()

    # GUARDRAIL
    if tool_results.get("forced_mode") == "guardrail":
        reason = tool_results.get("guardrail", {}).get("reason", "off-topic")
        return f"""\
I'm specialised in diet and nutrition, so that topic is a bit outside my expertise! 🙏
---A2UI_JSON---
[
  {{
    "surfaceUpdate": {{
      "surfaceId": "diet_surface",
      "components": [
        {{ "id": "root", "component": {{ "Column": {{ "children": ["guardrail"] }} }} }},
        {{
          "id": "guardrail",
          "component": {{
            "GuardrailCard": {{
              "message": {{ "path": "/guardrail/message" }},
              "suggestion": {{ "path": "/guardrail/suggestion" }}
            }}
          }}
        }}
      ]
    }}
  }},
  {{
    "dataModelUpdate": {{
      "surfaceId": "diet_surface",
      "contents": [
        {{
          "key": "guardrail",
          "valueMap": [
            {{ "key": "message", "valueString": "That topic is outside my area of expertise as an Indian Diet Planner. 🙏" }},
            {{ "key": "suggestion", "valueString": "I can help with meal plans, food substitutions, calorie questions, and Indian nutrition advice. What would you like to know about your diet?" }}
          ]
        }}
      ]
    }}
  }},
  {{ "beginRendering": {{ "surfaceId": "diet_surface", "root": "root" }} }}
]"""

    # INTERRUPT
    if tool_results.get("needs_interrupt"):
        food_result = tool_results.get("food_analysis", {})
        food_name = food_result.get("food_name", "this food")
        required_fields = food_result.get("required_fields", [])
        fields_json = _build_interrupt_fields_json(required_fields)

        return f"""\
Great question about {food_name}! To give you an accurate, personalised answer, I need just a couple of quick details.
---A2UI_JSON---
[
  {{
    "surfaceUpdate": {{
      "surfaceId": "diet_surface",
      "components": [
        {{ "id": "root", "component": {{ "Column": {{ "children": ["interrupt_form"] }} }} }},
        {{
          "id": "interrupt_form",
          "component": {{
            "ContextInterruptForm": {{
              "title": {{ "literalString": "Quick Check — About {food_name.title()}" }},
              "subtitle": {{ "literalString": "These details help me personalise the answer for you." }},
              "fields": {{ "path": "/interrupt/fields" }},
              "submitAction": {{ "literalString": "submit_interrupt_context" }},
              "pendingQuestion": {{ "literalString": "{message}" }}
            }}
          }}
        }}
      ]
    }}
  }},
  {{
    "dataModelUpdate": {{
      "surfaceId": "diet_surface",
      "contents": [
        {{
          "key": "interrupt",
          "valueMap": [
            {{
              "key": "fields",
              "valueMapList": {fields_json}
            }}
          ]
        }}
      ]
    }}
  }},
  {{ "beginRendering": {{ "surfaceId": "diet_surface", "root": "root" }} }}
]"""

    # INTAKE — no profile yet
    if not session.user_profile:
        goal_label = "Lose Weight"
        if "gain" in msg_lower:
            goal_label = "Gain Weight"
        elif "maintain" in msg_lower:
            goal_label = "Maintain Weight"
        elif "muscle" in msg_lower:
            goal_label = "Build Muscle"

        return f"""\
I'd love to help you with a personalised Indian diet plan! First, let me collect a few details about you.
---A2UI_JSON---
[
  {{
    "surfaceUpdate": {{
      "surfaceId": "diet_surface",
      "components": [
        {{ "id": "root", "component": {{ "Column": {{ "children": ["profile_form"] }} }} }},
        {{
          "id": "profile_form",
          "component": {{
            "UserProfileForm": {{
              "goal": {{ "literalString": "{goal_label}" }},
              "fields": {{ "path": "/form/fields" }},
              "submitAction": {{ "literalString": "submit_profile" }}
            }}
          }}
        }}
      ]
    }}
  }},
  {{
    "dataModelUpdate": {{
      "surfaceId": "diet_surface",
      "contents": [
        {{
          "key": "form",
          "valueMap": [
            {{
              "key": "fields",
              "valueMapList": [
                {{ "valueMap": [
                  {{ "key": "id", "valueString": "height_cm" }},
                  {{ "key": "label", "valueString": "Height (cm)" }},
                  {{ "key": "type", "valueString": "number" }},
                  {{ "key": "required", "valueBool": true }}
                ]}},
                {{ "valueMap": [
                  {{ "key": "id", "valueString": "weight_kg" }},
                  {{ "key": "label", "valueString": "Current Weight (kg)" }},
                  {{ "key": "type", "valueString": "number" }},
                  {{ "key": "required", "valueBool": true }}
                ]}},
                {{ "valueMap": [
                  {{ "key": "id", "valueString": "age" }},
                  {{ "key": "label", "valueString": "Age" }},
                  {{ "key": "type", "valueString": "number" }},
                  {{ "key": "required", "valueBool": true }}
                ]}},
                {{ "valueMap": [
                  {{ "key": "id", "valueString": "gender" }},
                  {{ "key": "label", "valueString": "Gender" }},
                  {{ "key": "type", "valueString": "select" }},
                  {{ "key": "options", "valueStringList": ["Male", "Female", "Other"] }},
                  {{ "key": "required", "valueBool": true }}
                ]}},
                {{ "valueMap": [
                  {{ "key": "id", "valueString": "dietary_preference" }},
                  {{ "key": "label", "valueString": "Dietary Preference" }},
                  {{ "key": "type", "valueString": "select" }},
                  {{ "key": "options", "valueStringList": ["Vegetarian", "Non-Vegetarian", "Vegan", "Jain", "Eggetarian"] }},
                  {{ "key": "required", "valueBool": true }}
                ]}},
                {{ "valueMap": [
                  {{ "key": "id", "valueString": "allergies" }},
                  {{ "key": "label", "valueString": "Any food allergies? (optional)" }},
                  {{ "key": "type", "valueString": "text" }},
                  {{ "key": "required", "valueBool": false }}
                ]}}
              ]
            }}
          ]
        }}
      ]
    }}
  }},
  {{ "beginRendering": {{ "surfaceId": "diet_surface", "root": "root" }} }}
]"""

    # PLAN_ACTIVE — generate or answer follow-up
    if session.user_profile and session.mode == AgentMode.PLAN_ACTIVE:
        return _generate_mock_diet_plan(session)

    # Fallback
    return """\
Namaste! I'm AaharAI, your personal Indian diet planning assistant. Tell me your health goal and I'll create a personalised diet plan for you!
---A2UI_JSON---
[]"""


def _build_interrupt_fields_json(required_fields: list) -> str:
    """Build the interrupt form fields JSON for required fields."""
    field_definitions = {
        "activity_level": {
            "label": "How active are you on most days?",
            "type": "select",
            "options": [
                "Sedentary (desk job, little movement)",
                "Lightly active (walks, light exercise)",
                "Moderately active (gym 3-4x/week)",
                "Very active (daily intense exercise)"
            ]
        },
        "cholesterol_history": {
            "label": "Any history of high cholesterol?",
            "type": "select",
            "options": ["No", "Yes", "Not sure / Never checked"]
        },
        "blood_sugar_history": {
            "label": "Any history of high blood sugar or diabetes?",
            "type": "select",
            "options": ["No", "Yes — Type 1", "Yes — Type 2", "Pre-diabetic", "Not sure"]
        },
        "blood_pressure_history": {
            "label": "Any history of high blood pressure?",
            "type": "select",
            "options": ["No", "Yes", "Borderline / monitoring", "Not sure"]
        },
        "caffeine_sensitivity": {
            "label": "How does caffeine usually affect you?",
            "type": "select",
            "options": ["Fine, no issues", "Mild sensitivity", "Strong sensitivity / avoid caffeine"]
        },
        "sleep_quality": {
            "label": "How would you describe your sleep?",
            "type": "select",
            "options": ["Good (7-9 hrs)", "Fair (5-6 hrs)", "Poor / trouble sleeping"]
        },
        "liver_history": {
            "label": "Any known liver conditions?",
            "type": "select",
            "options": ["No", "Yes", "Prefer not to say"]
        },
        "uric_acid_history": {
            "label": "Any history of high uric acid or gout?",
            "type": "select",
            "options": ["No", "Yes", "Not sure"]
        },
        "lactose_tolerance": {
            "label": "Any lactose intolerance?",
            "type": "select",
            "options": ["No, I tolerate dairy fine", "Mild intolerance", "Strong intolerance / avoid dairy"]
        }
    }

    result = []
    for field_id in required_fields:
        defn = field_definitions.get(field_id, {
            "label": field_id.replace("_", " ").title(),
            "type": "text",
            "options": []
        })

        field_map = [
            f'{{ "key": "id", "valueString": "{field_id}" }}',
            f'{{ "key": "label", "valueString": "{defn["label"]}" }}',
            f'{{ "key": "type", "valueString": "{defn["type"]}" }}',
        ]
        if defn.get("options"):
            opts = json.dumps(defn["options"])
            field_map.append(f'{{ "key": "options", "valueStringList": {opts} }}')

        result.append('{ "valueMap": [' + ", ".join(field_map) + "] }")

    return "[" + ", ".join(result) + "]"


def _generate_mock_diet_plan(session: SessionState) -> str:
    """Generate a mock diet plan response for demo purposes."""
    profile = session.user_profile
    plan_data = generate_diet_plan(
        goal=profile.goal,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        age=profile.age,
        gender=profile.gender,
        dietary_preference=profile.dietary_preference,
        allergies=profile.allergies
    )

    calorie_target = plan_data["calorie_target"]
    bmi = plan_data["bmi"]
    pref = profile.dietary_preference

    # Build meals based on dietary preference
    meals = _get_meals_for_preference(pref, profile.allergies, calorie_target)

    # Update session
    from schemas.session_state import DietPlan, MealSlot
    session.active_plan = DietPlan(
        goal=profile.goal,
        calorie_target=calorie_target,
        bmi=bmi,
        dietary_preference=pref,
        meals=[MealSlot(**m) for m in meals],
        hydration_tip="Drink 8-10 glasses of water daily. Start each morning with warm jeera water.",
        general_notes=[
            "Avoid fried snacks and maida-based items",
            "Use minimal oil — prefer cold-pressed mustard or coconut oil",
            "Eat dinner at least 2 hours before sleeping",
            "Chew food slowly and mindfully — it aids digestion"
        ]
    )

    meals_json = json.dumps([{
        "time": m["time"],
        "slot_name": m["slot_name"],
        "dish_name": m["dish_name"],
        "portion": m["portion"],
        "calories": m["calories"],
        "protein_g": m["protein_g"],
        "recipe_tip": m["recipe_tip"]
    } for m in meals], ensure_ascii=False)

    bmi_status = "Normal" if 18.5 <= bmi <= 24.9 else ("Underweight" if bmi < 18.5 else "Overweight")

    return f"""\
Here's your personalised Indian diet plan! Based on your profile, your daily calorie target is {calorie_target} kcal (BMI: {bmi} — {bmi_status}). Let's get started on your journey! 🥗
---A2UI_JSON---
[
  {{
    "surfaceUpdate": {{
      "surfaceId": "diet_surface",
      "components": [
        {{ "id": "root", "component": {{ "Column": {{ "children": ["plan_card"] }} }} }},
        {{
          "id": "plan_card",
          "component": {{
            "DietPlanCard": {{
              "goal": {{ "path": "/plan/goal" }},
              "calorie_target": {{ "path": "/plan/calorie_target" }},
              "bmi": {{ "path": "/plan/bmi" }},
              "dietary_preference": {{ "path": "/plan/dietary_preference" }},
              "meals": {{ "path": "/plan/meals" }},
              "hydration_tip": {{ "path": "/plan/hydration_tip" }},
              "general_notes": {{ "path": "/plan/general_notes" }}
            }}
          }}
        }}
      ]
    }}
  }},
  {{
    "dataModelUpdate": {{
      "surfaceId": "diet_surface",
      "contents": [
        {{
          "key": "plan",
          "valueMap": [
            {{ "key": "goal", "valueString": "{profile.goal}" }},
            {{ "key": "calorie_target", "valueInt": {calorie_target} }},
            {{ "key": "bmi", "valueFloat": {bmi} }},
            {{ "key": "dietary_preference", "valueString": "{pref}" }},
            {{ "key": "hydration_tip", "valueString": "Drink 8-10 glasses of water daily. Start each morning with warm jeera water." }},
            {{ "key": "general_notes", "valueStringList": [
              "Avoid fried snacks and maida-based items",
              "Use minimal oil — prefer cold-pressed mustard or coconut oil",
              "Eat dinner at least 2 hours before sleeping",
              "Chew food slowly — it aids digestion and reduces bloating"
            ]}},
            {{
              "key": "meals",
              "valueMapList": {_meals_to_valuemaplist(meals)}
            }}
          ]
        }}
      ]
    }}
  }},
  {{ "beginRendering": {{ "surfaceId": "diet_surface", "root": "root" }} }}
]"""


def _meals_to_valuemaplist(meals: list) -> str:
    """Convert meals list to A2UI valueMapList JSON string."""
    items = []
    for m in meals:
        items.append(
            '{ "valueMap": ['
            f'{{ "key": "time", "valueString": "{m["time"]}" }},'
            f'{{ "key": "slot_name", "valueString": "{m["slot_name"]}" }},'
            f'{{ "key": "dish_name", "valueString": {json.dumps(m["dish_name"])} }},'
            f'{{ "key": "portion", "valueString": {json.dumps(m["portion"])} }},'
            f'{{ "key": "calories", "valueInt": {m["calories"]} }},'
            f'{{ "key": "protein_g", "valueFloat": {m["protein_g"]} }},'
            f'{{ "key": "recipe_tip", "valueString": {json.dumps(m["recipe_tip"])} }}'
            '] }'
        )
    return '[' + ', '.join(items) + ']'


def _get_meals_for_preference(pref: str, allergies: list, calorie_target: int) -> list:
    """Get meal slots based on dietary preference."""
    pref_lower = pref.lower()

    if "jain" in pref_lower:
        return [
            {
                "time": "7:00 AM – 8:00 AM",
                "slot_name": "Morning Breakfast",
                "dish_name": "Besan Cheela with Lauki Chutney + 1 glass warm water",
                "portion": "2 medium cheelas (150g) + 2 tbsp chutney",
                "calories": 280,
                "protein_g": 10.0,
                "recipe_tip": "Use besan batter with carom seeds (ajwain) and green chilli. No onion or garlic."
            },
            {
                "time": "10:30 AM – 11:00 AM",
                "slot_name": "Mid-Morning Snack",
                "dish_name": "Roasted Makhana with Coconut Water",
                "portion": "1 handful makhana (30g) + 1 glass coconut water",
                "calories": 130,
                "protein_g": 4.0,
                "recipe_tip": "Roast makhana with rock salt and cumin. Avoid processed snacks."
            },
            {
                "time": "1:00 PM – 2:00 PM",
                "slot_name": "Lunch",
                "dish_name": "Turai Dal + 2 Phulkas + Lauki Sabzi",
                "portion": "1 katori dal + 2 phulkas + 1 katori sabzi",
                "calories": 420,
                "protein_g": 16.0,
                "recipe_tip": "Use toor dal with turai (ridge gourd). Avoid root vegetables entirely."
            },
            {
                "time": "4:00 PM – 5:00 PM",
                "slot_name": "Evening Snack",
                "dish_name": "Tinda Salad with Lemon + Chaas",
                "portion": "1 small bowl tinda + 1 glass chaas",
                "calories": 100,
                "protein_g": 5.0,
                "recipe_tip": "Tinda (apple gourd) is Jain-friendly and cooling. Add rock salt and cumin."
            },
            {
                "time": "7:00 PM – 8:00 PM",
                "slot_name": "Dinner",
                "dish_name": "Khichdi with Parwal Sabzi",
                "portion": "1 katori khichdi + 1 katori sabzi",
                "calories": 380,
                "protein_g": 14.0,
                "recipe_tip": "Make khichdi with moong dal and rice. Parwal (pointed gourd) is easily digestible."
            }
        ]
    elif "vegan" in pref_lower:
        return [
            {
                "time": "7:00 AM – 8:00 AM",
                "slot_name": "Morning Breakfast",
                "dish_name": "Poha with Peas and Roasted Peanuts + 1 glass lemon water",
                "portion": "1 medium bowl poha (150g) + 1 tbsp peanuts",
                "calories": 300,
                "protein_g": 9.0,
                "recipe_tip": "Use thin poha. Add mustard seeds, curry leaves, and a squeeze of lemon at the end."
            },
            {
                "time": "10:30 AM – 11:00 AM",
                "slot_name": "Mid-Morning Snack",
                "dish_name": "Sprouts Chaat with Coconut Chutney",
                "portion": "1 katori mixed sprouts + 2 tbsp chutney",
                "calories": 140,
                "protein_g": 9.0,
                "recipe_tip": "Soak moong and chana overnight and sprout for 24 hours. Rich in plant protein."
            },
            {
                "time": "1:00 PM – 2:00 PM",
                "slot_name": "Lunch",
                "dish_name": "Rajma Chawal with Salad (no ghee)",
                "portion": "1 katori rajma + 3/4 katori rice + 1 bowl salad",
                "calories": 480,
                "protein_g": 20.0,
                "recipe_tip": "Use cold-pressed mustard oil for tadka. Skip butter entirely — coconut milk makes it creamy."
            },
            {
                "time": "4:00 PM – 5:00 PM",
                "slot_name": "Evening Snack",
                "dish_name": "Roasted Chana with Jaggery Tea",
                "portion": "2 tbsp roasted chana + 1 glass herbal chai (no milk)",
                "calories": 120,
                "protein_g": 6.0,
                "recipe_tip": "Herbal chai with tulsi, ginger, and black pepper is warming and caffeine-free."
            },
            {
                "time": "7:00 PM – 8:00 PM",
                "slot_name": "Dinner",
                "dish_name": "Palak Dal + 2 Rotis (no ghee)",
                "portion": "1 katori palak moong dal + 2 medium rotis",
                "calories": 380,
                "protein_g": 15.0,
                "recipe_tip": "Use moong dal with blanched spinach. Drizzle with lemon instead of ghee for flavour."
            }
        ]
    elif "non-vegetarian" in pref_lower or "nonvegetarian" in pref_lower:
        return [
            {
                "time": "7:00 AM – 8:00 AM",
                "slot_name": "Morning Breakfast",
                "dish_name": "Egg Bhurji with 2 Rotis + Chai",
                "portion": "2 eggs bhurji + 2 medium rotis + 1 cup chai",
                "calories": 350,
                "protein_g": 18.0,
                "recipe_tip": "Use minimal oil. Add finely chopped tomato, green chilli, and coriander. Avoid butter."
            },
            {
                "time": "10:30 AM – 11:00 AM",
                "slot_name": "Mid-Morning Snack",
                "dish_name": "Sprouts Chaat with Lemon",
                "portion": "1 katori mixed sprouts + 1 tsp lemon",
                "calories": 120,
                "protein_g": 8.0,
                "recipe_tip": "Add chaat masala and fresh coriander for a flavour boost without extra calories."
            },
            {
                "time": "1:00 PM – 2:00 PM",
                "slot_name": "Lunch",
                "dish_name": "Grilled Chicken Curry + 2 Rotis + Cucumber Raita",
                "portion": "150g chicken + 2 rotis + 1 small katori raita",
                "calories": 520,
                "protein_g": 42.0,
                "recipe_tip": "Marinate chicken in curd and spices overnight. Grill or cook in minimal oil."
            },
            {
                "time": "4:00 PM – 5:00 PM",
                "slot_name": "Evening Snack",
                "dish_name": "Roasted Makhana + Buttermilk",
                "portion": "1 handful makhana + 1 glass chaas",
                "calories": 110,
                "protein_g": 5.0,
                "recipe_tip": "Spiced chaas with jeera, ginger, and mint helps with digestion after a protein-rich lunch."
            },
            {
                "time": "7:00 PM – 8:00 PM",
                "slot_name": "Dinner",
                "dish_name": "Fish Curry + 1 Roti + Steamed Vegetables",
                "portion": "150g fish + 1 roti + 1 katori veggies",
                "calories": 420,
                "protein_g": 35.0,
                "recipe_tip": "Use rohu or pomfret. Cook in a light tomato-based curry with minimal oil and kokum."
            }
        ]
    else:
        # Default vegetarian
        return [
            {
                "time": "7:00 AM – 8:00 AM",
                "slot_name": "Morning Breakfast",
                "dish_name": "Moong Dal Chilla with Green Chutney + Lemon Water",
                "portion": "2 medium chillas (150g) + 2 tbsp chutney + 1 glass water",
                "calories": 280,
                "protein_g": 12.5,
                "recipe_tip": "Add finely chopped spinach and ajwain to the batter for better digestion and iron."
            },
            {
                "time": "10:30 AM – 11:00 AM",
                "slot_name": "Mid-Morning Snack",
                "dish_name": "Roasted Makhana with Chaas",
                "portion": "1 handful makhana (30g) + 1 glass chaas (200ml)",
                "calories": 150,
                "protein_g": 5.0,
                "recipe_tip": "Roast makhana in a dry pan with rock salt and cumin. Chaas aids gut health."
            },
            {
                "time": "1:00 PM – 2:00 PM",
                "slot_name": "Lunch",
                "dish_name": "Dal Tadka + 2 Rotis + Baingan Sabzi + Kachumber Salad",
                "portion": "1 katori dal + 2 medium rotis + 1 katori sabzi + 1 small bowl salad",
                "calories": 480,
                "protein_g": 18.0,
                "recipe_tip": "Use toor dal with a tadka of mustard seeds, curry leaves, tomato, and minimal ghee."
            },
            {
                "time": "4:00 PM – 5:00 PM",
                "slot_name": "Evening Snack",
                "dish_name": "Sprouts Chaat with Lemon and Chaat Masala",
                "portion": "1 katori mixed sprouts + 1 tsp lemon juice",
                "calories": 120,
                "protein_g": 8.0,
                "recipe_tip": "Soak moong overnight and sprout for 24-36 hours. Raw sprouts have higher nutrient value."
            },
            {
                "time": "7:00 PM – 8:00 PM",
                "slot_name": "Dinner",
                "dish_name": "Palak Dal + 1 Roti + Cucumber Salad",
                "portion": "1 katori palak moong dal + 1 medium roti + 1 bowl salad",
                "calories": 360,
                "protein_g": 15.0,
                "recipe_tip": "Blanch spinach lightly before adding to dal. Eat dinner 2 hours before sleeping."
            }
        ]