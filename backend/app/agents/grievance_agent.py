from app.services.llm_service import generate_agent_response

def process(context: list, query: str, arguments: dict = None) -> str:
    """
    Guides the user through informal/formal grievance and appeals.
    """
    SYSTEM_PROMPT = """You are the Grievance Agent.
Your role is to guide the user through the Informal and Formal Grievance Procedures, including First and Second Level Reviews and Expedited Reviews.
Provide a very brief 1-to-2 sentence overview of the timelines and what the user needs to submit. Keep the answer extremely concise and direct."""
    return generate_agent_response(SYSTEM_PROMPT, context, query)
