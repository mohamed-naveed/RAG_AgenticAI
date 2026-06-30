from app.services.llm_service import generate_agent_response

SYSTEM_PROMPT = """You are the Policy RAG Agent.
Your role is to answer general questions about the insurance policy's definitions, scope of coverage, and basic terms.
Be concise and clear."""

def process(context: list, query: str) -> str:
    return generate_agent_response(SYSTEM_PROMPT, context, query)
