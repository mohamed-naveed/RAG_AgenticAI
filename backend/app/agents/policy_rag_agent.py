from app.services.llm_service import generate_agent_response

def process(context: list, query: str, arguments: dict = None) -> str:
    """
    Answers general policy questions.
    """
    SYSTEM_PROMPT = """You are the Policy RAG Agent.
Your role is to answer general questions about the insurance policy's definitions, scope of coverage, and basic terms.
Provide a very brief 1-to-2 sentence direct answer to the user's question."""
    return generate_agent_response(SYSTEM_PROMPT, context, query)
