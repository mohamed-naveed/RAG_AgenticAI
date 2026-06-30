from app.services.llm_service import query_llm

def route_query(query: str) -> str:
    """
    Classifies the user's query and routes it to the appropriate specialized agent using OpenRouter.
    Returns the name of the agent to use.
    """
    
    prompt = f"""
    You are the Router Agent for an Insurance RAG system handling an Accident Only Blanket Benefits Policy.
    Your job is to analyze the user's query and route it to ONE of the following specialized agents.
    
    Agents:
    1. policy_rag_agent: For general questions about policy definitions, scope of coverage, and basic terms.
    2. claim_eligibility_agent: For questions about whether a specific scenario is covered (e.g., accident vs sickness, time limits, sponsored activities).
    3. benefit_calculator_agent: For questions about specific numbers, maximum benefits, deductibles, coinsurance, and dollar amounts.
    4. exclusion_checker_agent: For questions about things that are specifically NOT covered, exclusions, acts of war, intoxication, non-school sports.
    5. grievance_agent: For questions about how to appeal a denied claim, grievance procedures, and expedited reviews.
    6. checklist_agent: For questions about what documents are needed to file a claim, claim forms, notice of claim, and proof of loss.
    
    User Query: "{query}"
    
    Respond with ONLY the exact name of the agent (e.g., "policy_rag_agent"). Do not include any other text, reasoning, or markdown.
    """
    
    try:
        response_text = query_llm(prompt)
        agent_name = response_text.strip().lower()
        
        valid_agents = [
            "policy_rag_agent", "claim_eligibility_agent", "benefit_calculator_agent",
            "exclusion_checker_agent", "grievance_agent", "checklist_agent"
        ]
        
        # Exact match or substring match fallback
        for valid in valid_agents:
            if valid in agent_name:
                return valid
                
        return "Unknown"  # Default fallback if LLM hallucinates
    except Exception as e:
        print(f"Error in Router Agent routing: {e}")
        return "Unknown"  # Safe default
