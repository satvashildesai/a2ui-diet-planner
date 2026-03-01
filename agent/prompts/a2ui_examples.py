INTAKE_EXAMPLE = """
=== EXAMPLE: INTAKE MODE ===
User: "I want to lose weight"
Session: { mode: "intake", userProfile: null }

CONVERSATIONAL TEXT: "I'd love to help you with a personalised Indian diet
plan! First, I need a few details about you."
---A2UI_JSON---
[
  {
    "surfaceUpdate": {
      "surfaceId": "diet_surface",
      "components": [
        { "id": "root", "component": { "Column": { "children": ["profile_form"] } } },
        {
          "id": "profile_form",
          "component": {
            "UserProfileForm": {
              "goal": { "literalString": "Lose Weight" },
              "fields": { "path": "/form/fields" },
              "submitAction": { "literalString": "submit_profile" }
            }
          }
        }
      ]
    }
  },
  {
    "dataModelUpdate": {
      "surfaceId": "diet_surface",
      "contents": [
        {
          "key": "form",
          "valueMap": [
            {
              "key": "fields",
              "valueMapList": [
                { "valueMap": [
                  { "key": "id", "valueString": "height_cm" },
                  { "key": "label", "valueString": "Height (cm)" },
                  { "key": "type", "valueString": "number" },
                  { "key": "required", "valueBool": true }
                ]},
                { "valueMap": [
                  { "key": "id", "valueString": "weight_kg" },
                  { "key": "label", "valueString": "Current Weight (kg)" },
                  { "key": "type", "valueString": "number" },
                  { "key": "required", "valueBool": true }
                ]},
                { "valueMap": [
                  { "key": "id", "valueString": "age" },
                  { "key": "label", "valueString": "Age" },
                  { "key": "type", "valueString": "number" },
                  { "key": "required", "valueBool": true }
                ]},
                { "valueMap": [
                  { "key": "id", "valueString": "gender" },
                  { "key": "label", "valueString": "Gender" },
                  { "key": "type", "valueString": "select" },
                  { "key": "options", "valueStringList": ["Male", "Female", "Other"] },
                  { "key": "required", "valueBool": true }
                ]},
                { "valueMap": [
                  { "key": "id", "valueString": "dietary_preference" },
                  { "key": "label", "valueString": "Dietary Preference" },
                  { "key": "type", "valueString": "select" },
                  { "key": "options", "valueStringList": [
                    "Vegetarian", "Non-Vegetarian", "Vegan", "Jain", "Eggetarian"
                  ]},
                  { "key": "required", "valueBool": true }
                ]},
                { "valueMap": [
                  { "key": "id", "valueString": "allergies" },
                  { "key": "label", "valueString": "Any food allergies? (optional)" },
                  { "key": "type", "valueString": "text" },
                  { "key": "required", "valueBool": false }
                ]}
              ]
            }
          ]
        }
      ]
    }
  },
  { "beginRendering": { "surfaceId": "diet_surface", "root": "root" } }
]
"""

PLAN_ACTIVE_EXAMPLE = """
=== EXAMPLE: PLAN_ACTIVE MODE — Diet Plan Generation ===
Triggered after profile form submission.

CONVERSATIONAL TEXT: "Here's your personalised Indian diet plan! Based on
your profile, your daily target is 1,480 kcal. Let's get started."
---A2UI_JSON---
[
  {
    "surfaceUpdate": {
      "surfaceId": "diet_surface",
      "components": [
        { "id": "root", "component": { "Column": { "children": ["plan_card"] } } },
        {
          "id": "plan_card",
          "component": {
            "DietPlanCard": {
              "goal": { "path": "/plan/goal" },
              "calorie_target": { "path": "/plan/calorie_target" },
              "bmi": { "path": "/plan/bmi" },
              "dietary_preference": { "path": "/plan/dietary_preference" },
              "meals": { "path": "/plan/meals" },
              "hydration_tip": { "path": "/plan/hydration_tip" },
              "general_notes": { "path": "/plan/general_notes" }
            }
          }
        }
      ]
    }
  },
  {
    "dataModelUpdate": {
      "surfaceId": "diet_surface",
      "contents": [
        {
          "key": "plan",
          "valueMap": [
            { "key": "goal", "valueString": "lose_weight" },
            { "key": "calorie_target", "valueInt": 1480 },
            { "key": "bmi", "valueFloat": 24.2 },
            { "key": "dietary_preference", "valueString": "Vegetarian" },
            { "key": "hydration_tip", "valueString": "Drink 8-10 glasses of water. Start mornings with warm jeera water." },
            { "key": "general_notes", "valueStringList": [
              "Avoid fried snacks and maida-based items",
              "Use minimal oil — prefer mustard or cold-pressed coconut oil",
              "Eat dinner at least 2 hours before sleeping"
            ]},
            {
              "key": "meals",
              "valueMapList": [
                { "valueMap": [
                  { "key": "time", "valueString": "7:00 AM – 8:00 AM" },
                  { "key": "slot_name", "valueString": "Morning Breakfast" },
                  { "key": "dish_name", "valueString": "Moong Dal Chilla with Green Chutney + 1 glass warm water with lemon" },
                  { "key": "portion", "valueString": "2 medium chillas (150g) + 2 tbsp chutney" },
                  { "key": "calories", "valueInt": 280 },
                  { "key": "protein_g", "valueFloat": 12.5 },
                  { "key": "recipe_tip", "valueString": "Add finely chopped spinach and ajwain to the batter for better digestion." }
                ]},
                { "valueMap": [
                  { "key": "time", "valueString": "10:30 AM – 11:00 AM" },
                  { "key": "slot_name", "valueString": "Mid-Morning Snack" },
                  { "key": "dish_name", "valueString": "Roasted Makhana with Chaas" },
                  { "key": "portion", "valueString": "1 handful makhana (30g) + 1 glass chaas (200ml)" },
                  { "key": "calories", "valueInt": 150 },
                  { "key": "protein_g", "valueFloat": 5.0 },
                  { "key": "recipe_tip", "valueString": "Roast makhana in a dry pan with a pinch of rock salt and cumin." }
                ]},
                { "valueMap": [
                  { "key": "time", "valueString": "1:00 PM – 2:00 PM" },
                  { "key": "slot_name", "valueString": "Lunch" },
                  { "key": "dish_name", "valueString": "Dal Tadka + 2 Rotis + Cucumber Raita" },
                  { "key": "portion", "valueString": "1 katori dal + 2 medium rotis + 1 small katori raita" },
                  { "key": "calories", "valueInt": 450 },
                  { "key": "protein_g", "valueFloat": 18.0 },
                  { "key": "recipe_tip", "valueString": "Use toor dal with a light tadka of mustard seeds, curry leaves and tomato." }
                ]},
                { "valueMap": [
                  { "key": "time", "valueString": "4:00 PM – 5:00 PM" },
                  { "key": "slot_name", "valueString": "Evening Snack" },
                  { "key": "dish_name", "valueString": "Sprouts Chaat with Lemon" },
                  { "key": "portion", "valueString": "1 katori mixed sprouts + 1 tsp lemon juice" },
                  { "key": "calories", "valueInt": 120 },
                  { "key": "protein_g", "valueFloat": 8.0 },
                  { "key": "recipe_tip", "valueString": "Add finely chopped onion, tomato, green chilli and chaat masala for flavour." }
                ]},
                { "valueMap": [
                  { "key": "time", "valueString": "7:00 PM – 8:00 PM" },
                  { "key": "slot_name", "valueString": "Dinner" },
                  { "key": "dish_name", "valueString": "Palak Dal + 1 Roti + Salad" },
                  { "key": "portion", "valueString": "1 katori palak dal + 1 medium roti + 1 small bowl salad" },
                  { "key": "calories", "valueInt": 380 },
                  { "key": "protein_g", "valueFloat": 15.0 },
                  { "key": "recipe_tip", "valueString": "Use moong dal with blanched spinach. Keep dinner light and easy to digest." }
                ]}
              ]
            }
          ]
        }
      ]
    }
  },
  { "beginRendering": { "surfaceId": "diet_surface", "root": "root" } }
]
"""

INTERRUPT_EXAMPLE = """
=== EXAMPLE: INTERRUPT MODE ===
User: "Is ghee good or bad for me?"
Session: { mode: "plan_active", userProfile: {...}, activePlan: {...} }
food_analyzer() returns: { needs_context: true, required_fields: ["activity_level", "cholesterol_history"] }

CONVERSATIONAL TEXT: "Great question about ghee! To give you an accurate
answer for your specific situation, I need two quick details."
---A2UI_JSON---
[
  {
    "surfaceUpdate": {
      "surfaceId": "diet_surface",
      "components": [
        { "id": "root", "component": { "Column": { "children": ["interrupt_form"] } } },
        {
          "id": "interrupt_form",
          "component": {
            "ContextInterruptForm": {
              "title": { "literalString": "Quick Check — About Ghee" },
              "subtitle": { "literalString": "These details help me personalise the answer for you." },
              "fields": { "path": "/interrupt/fields" },
              "submitAction": { "literalString": "submit_interrupt_context" },
              "pendingQuestion": { "literalString": "Is ghee good or bad for me?" }
            }
          }
        }
      ]
    }
  },
  {
    "dataModelUpdate": {
      "surfaceId": "diet_surface",
      "contents": [
        {
          "key": "interrupt",
          "valueMap": [
            {
              "key": "fields",
              "valueMapList": [
                { "valueMap": [
                  { "key": "id", "valueString": "activity_level" },
                  { "key": "label", "valueString": "How active are you on most days?" },
                  { "key": "type", "valueString": "select" },
                  { "key": "options", "valueStringList": [
                    "Sedentary (desk job, little movement)",
                    "Lightly active (walks, light exercise)",
                    "Moderately active (gym 3-4x/week)",
                    "Very active (daily intense exercise)"
                  ]}
                ]},
                { "valueMap": [
                  { "key": "id", "valueString": "cholesterol_history" },
                  { "key": "label", "valueString": "Any history of high cholesterol?" },
                  { "key": "type", "valueString": "select" },
                  { "key": "options", "valueStringList": ["No", "Yes", "Not sure / Never checked"] }
                ]}
              ]
            }
          ]
        }
      ]
    }
  },
  { "beginRendering": { "surfaceId": "diet_surface", "root": "root" } }
]
"""

GUARDRAIL_EXAMPLE = """
=== EXAMPLE: GUARDRAIL MODE ===
User: "Who won the IPL this year?"
guardrail_checker() returns: { is_relevant: false, reason: "cricket" }

CONVERSATIONAL TEXT: ""
---A2UI_JSON---
[
  {
    "surfaceUpdate": {
      "surfaceId": "diet_surface",
      "components": [
        { "id": "root", "component": { "Column": { "children": ["guardrail"] } } },
        {
          "id": "guardrail",
          "component": {
            "GuardrailCard": {
              "message": { "path": "/guardrail/message" },
              "suggestion": { "path": "/guardrail/suggestion" }
            }
          }
        }
      ]
    }
  },
  {
    "dataModelUpdate": {
      "surfaceId": "diet_surface",
      "contents": [
        {
          "key": "guardrail",
          "valueMap": [
            { "key": "message", "valueString": "I'm specialised in diet and nutrition, so IPL scores are a bit outside my expertise! 🙏" },
            { "key": "suggestion", "valueString": "I can help you with your meal plan, food substitutions, calorie questions, or nutritional advice. What would you like to know?" }
          ]
        }
      ]
    }
  },
  { "beginRendering": { "surfaceId": "diet_surface", "root": "root" } }
]
"""

ALL_EXAMPLES = INTAKE_EXAMPLE + PLAN_ACTIVE_EXAMPLE + INTERRUPT_EXAMPLE + GUARDRAIL_EXAMPLE
