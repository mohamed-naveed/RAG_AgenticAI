from app.services.llm_service import query_llm
import json

def route_query(query: str) -> str:
    """
    Classifies the user's query and routes it to the appropriate specialized agent using OpenRouter Tool Calling.
    """
    
    # 1. Define the routing function tool schema
    tools = [
        {
            "type": "function",
            "function": {
                "name": "route_to_agent",
                "description": "Routes the user's query to the single most appropriate specialized insurance agent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "The exact name of the agent chosen to handle the question.",
                            "enum": [
                                "policy_rag_agent",
                                "claim_eligibility_agent",
                                "benefit_calculator_agent",
                                "exclusion_checker_agent",
                                "grievance_agent",
                                "checklist_agent"
                            ]
                        }
                    },
                    "required": ["agent_name"]
                }
            }
        }
    ]
    
    # Force the model to call this specific function
    tool_choice = {
        "type": "function",
        "function": {"name": "route_to_agent"}
    }
    
    prompt = f"""
    You are the Router Agent for an Insurance RAG system handling an Accident Only Blanket Benefits Policy.
    Analyze the user's query and decide which agent should handle it.
    
    Agent Descriptions:
    - policy_rag_agent: General policy definitions, terminology, contacts, or basic terms.
    - claim_eligibility_agent: Determines if a specific claim or scenario is covered (e.g. accident vs sickness, time limits, sponsored activities).
    - benefit_calculator_agent: Handles pricing tables, copays, deductibles, coinsurance, and specific dollar limits.
    - exclusion_checker_agent: Checks for things explicitly NOT covered (exclusions like acts of war, intoxication, non-school sports).
    - grievance_agent: Explains the appeals process, informal/formal dispute resolution steps, and grievance timelines.
    - checklist_agent: Tells the user exactly what documents are needed to file a claim.
    
    User Query: "{query}"
    """
    
    try:
        # Query LLM with the tool schema
        response = query_llm(prompt, tools=tools, tool_choice=tool_choice)
        
        # Check if the LLM returned a structured tool call
        if isinstance(response, dict) and 'tool_calls' in response:
            tool_call = response['tool_calls'][0]
            arguments = tool_call.get('function', {}).get('arguments', '{}')
            
            # Arguments can be a stringified JSON or a dict directly depending on client parsing
            if isinstance(arguments, str):
                parsed_args = json.loads(arguments)
            else:
                parsed_args = arguments
                
            routed_agent = parsed_args.get('agent_name', 'policy_rag_agent')
            print(f"Router Agent dynamically selected tool: {routed_agent}")
            return routed_agent
            
        # Fallback if no tool call was returned (e.g. error or string fallback)
        print(f"Router Agent fallback (no tool call): {response}")
        return "policy_rag_agent"
        
    except Exception as e:
        print(f"Error in Router Agent tool routing: {e}")
        return "policy_rag_agent"
