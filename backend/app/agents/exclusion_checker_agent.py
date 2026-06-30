from app.services.llm_service import generate_agent_response

def process(context: list, query: str, arguments: dict = None) -> str:
    """
    Checks if the scenario falls under any exclusions and returns structured JSON.
    """
    args = arguments or {}
    
    SYSTEM_PROMPT = f"""You are the Exclusion Checker Agent.
Your role is to check if a specific scenario falls under exclusions like intoxication, acts of war, cosmetic surgery, non-school sports.

Scenario Details Extracted:
- Scenario: {args.get('scenario_details', 'Not specified')}

Check the 'Exclusions' and 'Additional Exclusions' sections of the policy in the provided context.

Provide a very brief 1-to-2 sentence direct conversational answer regarding whether the scenario is excluded. Include citations to the source pages from the context."""
    return generate_agent_response(SYSTEM_PROMPT, context, query)
