from app.services.llm_service import generate_agent_response

def process(context: list, query: str, arguments: dict = None) -> str:
    """
    Calculates the payable benefit amount based on limits and outputs structured JSON.
    """
    args = arguments or {}
    bill_amount = args.get('bill_amount', 0.0)
    
    SYSTEM_PROMPT = f"""You are the Benefit Calculator Agent.
Your role is to calculate estimated payable amounts based on bill values and policy limits.

Input Details:
- Bill Amount: {bill_amount}
- Benefit Type: {args.get('benefit_type', 'Not specified')}

Look up the 'Schedule of Benefits' section in the provided context for the specified benefit type (e.g. Emergency Room, Hospital Room & Board, Surgical, Physiotherapy, Prescription Drugs, etc.). Apply deductibles, coinsurance, and per-visit or per-injury limits.

Provide a very brief 1-to-2 sentence direct conversational calculation of the payable benefit amount. Include citations to the source pages from the context."""
    return generate_agent_response(SYSTEM_PROMPT, context, query)
