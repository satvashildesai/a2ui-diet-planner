from pydantic import BaseModel
from typing import Optional, Literal
from enum import Enum

class AgentMode(str, Enum):
    INTAKE = "intake"
    PLAN_ACTIVE = "plan_active"
    INTERRUPT_PENDING = "interrupt_pending"
    GUARDRAIL = "guardrail"

class UserProfile(BaseModel):
    height_cm: float
    weight_kg: float
    age: int
    gender: str
    dietary_preference: str
    allergies: list[str] = []
    goal: str

class MealSlot(BaseModel):
    time: str
    slot_name: str
    dish_name: str
    portion: str
    calories: int
    protein_g: float
    recipe_tip: str

class DietPlan(BaseModel):
    goal: str
    calorie_target: int
    bmi: float
    dietary_preference: str
    meals: list[MealSlot]
    hydration_tip: str
    general_notes: list[str]

class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: str

class SessionState(BaseModel):
    session_id: str
    mode: AgentMode = AgentMode.INTAKE
    user_profile: Optional[UserProfile] = None
    active_plan: Optional[DietPlan] = None
    pending_question: Optional[str] = None
    conversation_history: list[ConversationMessage] = []
