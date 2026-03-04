# AaharAI — AI-Driven Indian Diet Planner

A culturally intelligent Indian diet planning web application powered by **Google ADK + Gemini 2.5 Flash** and the **A2UI framework** for dynamic, adaptive UIs.

---

## Features

- **Adaptive UI** — Agent-generated interfaces, never predetermined forms
- **4 Agent Modes**: Intake → Plan Active → Context Interrupt → Guardrail
- **Real Indian Dishes** — Moong Dal Chilla, Dal Tadka, Rajma Chawal, and more
- **Dietary Intelligence** — Vegetarian, Vegan, Jain (no root vegetables!), Non-Veg, Eggetarian
- **Context Interrupt** — Ghee question? Agent pauses, collects your cholesterol history, then answers
- **Guardrail** — Off-topic queries are warmly redirected to diet topics
- **Streaming SSE** — Real-time agent responses via Server-Sent Events
- **Mock Mode** — Full functionality without a Gemini API key (for development)

---

## Architecture

```
User Message
     │
     ▼
guardrail_checker()  ← Always called FIRST
     │
 ┌───┴────────────────────┐
 ▼                        ▼
OFF-TOPIC              RELEVANT
 │                        │
 ▼                  session.mode?
GuardrailCard   ┌────────┼──────────────┐
                ▼        ▼              ▼
             INTAKE  PLAN_ACTIVE  INTERRUPT_PENDING
                │        │              │
                ▼        ▼              ▼
          UserProfile  Follow-up    Resume with
          Form         answer or    new context
                       INTERRUPT
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent | Google ADK + Gemini 2.5 Flash |
| Backend | FastAPI + SSE (Server-Sent Events) |
| Frontend | React 18 + TypeScript + Vite |
| UI Protocol | A2UI v0.8 (Google open-source) |
| Styling | Tailwind CSS v3 |
| State | Zustand |
| Forms | React Hook Form + Zod |

---

## Quick Start

### Option 1: Standalone HTML (No install needed)

Open `frontend/index.html` directly in a browser. Full agent simulation runs in-browser — no backend required.

### Option 2: Full Stack with Docker Compose

```bash
# 1. Clone / copy the project
cd indian-diet-planner

# 2. Set up environment (optional - app works without it)
cp .env.example .env
# Add your GEMINI_API_KEY from https://aistudio.google.com/

# 3. Start everything
docker-compose up

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

### Option 3: Local Development

**Backend:**
```bash
cd agent
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here  # optional
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

---

## Project Structure

```
indian-diet-planner/
├── agent/
│   ├── main.py                    # FastAPI endpoints + SSE
│   ├── diet_agent.py              # Core agent logic + mock mode
│   ├── tools/
│   │   ├── guardrail_checker.py   # Off-topic detection (always first)
│   │   ├── diet_plan_generator.py # BMR/TDEE calculation
│   │   ├── food_analyzer.py       # Context-sensitive food analysis
│   │   └── context_evaluator.py   # Session state evaluation
│   ├── prompts/
│   │   ├── system_prompt.py       # Master agent instructions
│   │   └── a2ui_examples.py       # Few-shot A2UI JSON examples
│   ├── schemas/
│   │   └── session_state.py       # Pydantic session schemas
│   └── requirements.txt
│
├── frontend/
│   ├── index.html                 # ← STANDALONE DEMO (works without install)
│   ├── src/
│   │   ├── catalog/
│   │   │   ├── index.ts           # A2UI component registry
│   │   │   ├── UserProfileForm.tsx
│   │   │   ├── DietPlanCard.tsx
│   │   │   ├── ContextInterruptForm.tsx
│   │   │   └── components.tsx     # GuardrailCard, NutritionBadge, etc.
│   │   ├── components/
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatBubble.tsx
│   │   │   └── DisclaimerBanner.tsx
│   │   ├── hooks/
│   │   │   └── useAgentSSE.ts     # SSE stream consumer
│   │   ├── store/
│   │   │   └── dietStore.ts       # Zustand global state
│   │   ├── A2UISurface.tsx        # A2UI message renderer
│   │   └── App.tsx
│   └── package.json
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/session` | Create new session → `{ session_id }` |
| POST | `/api/chat` | SSE stream: user message → A2UI chunks |
| POST | `/api/action` | SSE stream: form submissions, actions |
| GET | `/api/session/{id}` | Get session info |

### Action Types

- `submit_profile` — Profile form submission → transitions to PLAN_ACTIVE, generates plan
- `submit_interrupt_context` — Context form → resumes pending question with new data
- `restart` — Reset session to INTAKE mode

---

## Indian Diet Plan Rules

The agent strictly enforces:

1. **Real dish names** — Never "Protein Source". Always "Moong Dal Chilla" or "Dal Tadka + Roti"
2. **Dietary preference is inviolable**:
   - Jain → Zero root vegetables (no potato, onion, garlic, carrot, beetroot)
   - Vegan → No dairy whatsoever (no ghee, paneer, dahi, butter, milk)
   - Vegetarian → No meat, fish, eggs
3. **Exactly 5 meals**: Breakfast (7am), Mid-Morning (10:30am), Lunch (1pm), Evening Snack (4pm), Dinner (7pm)
4. **Indian portions**: katori, tablespoon, glass, handful — not cups/ounces
5. **Allergies strictly enforced** — cross-checked against every dish

---

## Test Scenarios

| Scenario | Expected Behaviour |
|----------|-------------------|
| "I want to lose weight" | UserProfileForm appears |
| Profile submitted (Vegetarian) | DietPlanCard with 5 real vegetarian Indian meals |
| Profile submitted (Jain) | Plan with NO root vegetables |
| "Is ghee good for me?" | ContextInterruptForm for cholesterol + activity |
| "Is ghee good for me?" + context submitted | Personalised ghee analysis |
| "Who won the IPL?" | GuardrailCard |
| "What movies are trending?" | GuardrailCard |
| "Can I eat heavier for lunch?" | Context-aware plan follow-up |

---

## With Gemini API

Add your free Gemini API key to unlock the real LLM:

1. Get key at https://aistudio.google.com/apikey (free tier)
2. Add to `.env`: `GEMINI_API_KEY=AIza...`
3. The agent switches from mock mode to Gemini 2.5 Flash automatically

Without a key, the app uses a deterministic mock that demonstrates all 4 agent modes.

---

## Notes

- Sessions are **ephemeral** — no database, no persistence
- Streaming is **always on** — responses stream in real-time via SSE
- The disclaimer banner is rendered by the app shell, **never** by the agent
- All 8 catalog components are registered and renderable
