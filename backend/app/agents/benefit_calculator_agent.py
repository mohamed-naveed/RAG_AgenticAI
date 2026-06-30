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

You MUST respond with a strictly formatted JSON object matching the schema below.
Do not output any markdown formatting (like ```json), explanation, or other text outside the JSON block.

JSON Schema:
{{
  "bill_amount": {bill_amount},
  "limit_applied": 0.0,  // The benefit limit found in the policy (e.g. 185.00), or null if no limit
  "estimated_payable_amount": 0.0, // The final estimated payable amount after applying coinsurance and deductibles
  "reason": "One-sentence concise explanation of the calculation and limits applied, citing the page number"
}}
"""
    return generate_agent_response(SYSTEM_PROMPT, context, query)
