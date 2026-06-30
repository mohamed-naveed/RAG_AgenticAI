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

You MUST respond with a strictly formatted JSON object matching the schema below.
Do not output any markdown formatting (like ```json), explanation, or other text outside the JSON block.

JSON Schema:
{{
  "status": "Excluded",  // Choose "Excluded", "Not Excluded", or "Manual Review Required"
  "reason": "One-sentence concise explanation of why it is excluded or not, citing the page number"
}}
"""
    return generate_agent_response(SYSTEM_PROMPT, context, query)
