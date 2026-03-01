def guardrail_checker(query: str) -> dict:
    """
    Checks if the query is relevant to diet, nutrition, food, fitness, or health.
    Returns: { "is_relevant": bool, "reason": str }
    Always call this FIRST before any other tool.
    """
    off_topic_keywords = [
        "cricket", "movie", "election", "stock", "code", "python tutorial",
        "relationship", "girlfriend", "travel", "hotel", "weather",
        "politics", "actor", "singer", "game", "series", "netflix",
        "ipl", "football", "match", "score", "song", "music", "news",
        "bitcoin", "crypto", "investment", "loan", "visa", "passport"
    ]
    query_lower = query.lower()
    for kw in off_topic_keywords:
        if kw in query_lower:
            return {"is_relevant": False, "reason": f"Query appears to be about '{kw}'"}
    return {"is_relevant": True, "reason": "Query is diet/health related"}