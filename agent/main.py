import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, uuid
from diet_agent import run_diet_agent
from schemas.session_state import SessionState, AgentMode, UserProfile

app = FastAPI(title="AaharAI - Indian Diet Planner", version="0.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

sessions: dict[str, SessionState] = {}  # Ephemeral — no DB


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ActionRequest(BaseModel):
    session_id: str
    action_name: str
    context: dict


@app.get("/")
def root():
    return {"status": "ok", "service": "AaharAI Indian Diet Planner", "version": "1.0.0"}


@app.post("/api/session")
def create_session():
    sid = str(uuid.uuid4())
    sessions[sid] = SessionState(session_id=sid)
    return {"session_id": sid}


@app.get("/api/session/{session_id}")
def get_session(session_id: str):
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}
    return {
        "session_id": session.session_id,
        "mode": session.mode.value,
        "has_profile": session.user_profile is not None,
        "has_plan": session.active_plan is not None,
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    session = sessions.get(req.session_id)
    if not session:
        return {"error": "Session not found"}

    async def stream():
        async for chunk in run_diet_agent(req.message, session):
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/api/action")
async def handle_action(req: ActionRequest):
    session = sessions.get(req.session_id)
    if not session:
        return {"error": "Session not found"}

    async def stream():
        if req.action_name == "submit_profile":
            # Handle allergies field - may come as comma-separated string
            context = req.context.copy()
            allergies_raw = context.get("allergies", "")
            if isinstance(allergies_raw, str) and allergies_raw.strip():
                context["allergies"] = [a.strip() for a in allergies_raw.split(",") if a.strip()]
            else:
                context["allergies"] = []

            # Coerce numeric fields
            for field in ["height_cm", "weight_kg"]:
                if field in context:
                    context[field] = float(context[field])
            if "age" in context:
                context["age"] = int(context["age"])

            # Map goal from display label to internal key
            goal_map = {
                "Lose Weight": "lose_weight",
                "Gain Weight": "gain_weight",
                "Build Muscle": "gain_weight",
                "Maintain Weight": "maintain_weight",
                "maintain_weight": "maintain_weight",
                "lose_weight": "lose_weight",
                "gain_weight": "gain_weight",
            }
            goal_raw = context.get("goal", "maintain_weight")
            context["goal"] = goal_map.get(goal_raw, "maintain_weight")

            session.user_profile = UserProfile(**context)
            session.mode = AgentMode.PLAN_ACTIVE

            async for chunk in run_diet_agent(
                f"Generate my personalised Indian diet plan. My goal is to {context['goal'].replace('_', ' ')}.",
                session
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        elif req.action_name == "submit_interrupt_context":
            session.mode = AgentMode.PLAN_ACTIVE
            pending = session.pending_question or req.context.get("pending_question", "")
            session.pending_question = None

            async for chunk in run_diet_agent(
                pending, session, additional_context=req.context
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        elif req.action_name == "restart":
            sessions[req.session_id] = SessionState(session_id=req.session_id)
            yield f"data: {json.dumps({'type': 'reset'})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")