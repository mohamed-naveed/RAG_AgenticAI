from app.services.llm_service import generate_agent_response

def process(context: list, query: str, arguments: dict = None) -> str:
    """
    Evaluates claim eligibility and returns a structured JSON payload.
    """
    args = arguments or {}
    
    SYSTEM_PROMPT = f"""You are the Claim Eligibility Agent.
Your role is to determine if a specific scenario or claim is eligible for coverage under this policy.

Claim Details Extracted:
- Person Type: {args.get('person_type', 'Not specified')}
- Activity Type: {args.get('activity_type', 'Not specified')}
- Accident Date: {args.get('accident_date', 'Not specified')}
- Treatment Type: {args.get('treatment_type', 'Not specified')}
- Injury Details: {args.get('injury_details', 'Not specified')}
- Claim Date: {args.get('claim_date', 'Not specified')}
- Other Insurance Exists: {args.get('other_insurance_exists', 'Not specified')}

Check:
1. If the person type is an eligible student on file (e.g. daycare, summer, community training program).
2. If the accident happened during a sponsored and supervised activity.
3. If it was an accident (sickness/disease is not covered).
4. If exclusions apply.

Provide a very brief 1-to-2 sentence direct conversational answer regarding claim eligibility. Include citations to the source pages from the context."""
    return generate_agent_response(SYSTEM_PROMPT, context, query)
