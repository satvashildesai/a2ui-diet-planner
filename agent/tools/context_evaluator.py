def context_evaluator(session_state: dict) -> dict:
    """
    Evaluates what context is available vs. what might be needed.
    Helps the agent understand the current mode and available data.
    Returns a summary of the current session context.
    """
    mode = session_state.get("mode", "intake")
    has_profile = session_state.get("user_profile") is not None
    has_plan = session_state.get("active_plan") is not None
    pending_question = session_state.get("pending_question")

    return {
        "current_mode": mode,
        "has_user_profile": has_profile,
        "has_active_plan": has_plan,
        "has_pending_question": pending_question is not None,
        "pending_question": pending_question,
        "can_answer_followup": has_profile and has_plan,
        "needs_profile_first": not has_profile,
    }