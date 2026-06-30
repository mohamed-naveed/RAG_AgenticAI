from app.services.llm_service import generate_agent_response

SYSTEM_PROMPT = """You are the Document Checklist Agent.
Your role is to tell the user exactly what documents and actions are required to file a claim based on the 'Claim Provisions' section.
Focus on Notice of Claim (within 30 days) and Proof of Loss (within 90 days). Present ONLY the raw checklist as a very short, clean bulleted list. Do not write any conversational intro or outro text."""

def process(context: list, query: str) -> str:
    return generate_agent_response(SYSTEM_PROMPT, context, query)
