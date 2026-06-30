from app.services.llm_service import query_llm
import json

def route_query(query: str) -> tuple[str, dict]:
    """
    Analyzes the user's query and routes it to the correct specialist agent "tool,"
    extracting the required arguments from the user's query text.
    
    Returns a tuple of (agent_name, extracted_arguments).
    """
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "policy_rag_agent",
                "description": "Answers general questions about the policy definitions, scope, or basic terms.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The general question or term the user wants defined or explained."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "claim_eligibility_agent",
                "description": "Evaluates if a specific person, scenario, or incident is likely eligible for coverage under the policy rules.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "person_type": {
                            "type": "string",
                            "description": "The type of person making the claim (e.g., student, child, teacher, guest)."
                        },
                        "activity_type": {
                            "type": "string",
                            "description": "The activity during which the incident happened (e.g., school sports, summer program, day care)."
                        },
                        "accident_date": {
                            "type": "string",
                            "description": "The date when the accident occurred."
                        },
                        "treatment_type": {
                            "type": "string",
                            "description": "The type of treatment received (e.g., physiotherapy, surgery, doctor visit)."
                        },
                        "injury_details": {
                            "type": "string",
                            "description": "Specific details of the injury (e.g., broken wrist, sprained ankle)."
                        },
                        "claim_date": {
                            "type": "string",
                            "description": "The date when the claim is being submitted."
                        },
                        "other_insurance_exists": {
                            "type": "boolean",
                            "description": "Whether the claimant has other primary health/accident insurance."
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "benefit_calculator_agent",
                "description": "Calculates estimated payable amounts based on bill values and policy limits.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bill_amount": {
                            "type": "number",
                            "description": "The raw bill amount charged by the provider (e.g., 500.00)."
                        },
                        "benefit_type": {
                            "type": "string",
                            "description": "The category of the medical benefit requested.",
                            "enum": [
                                "emergency_room",
                                "hospital_room_and_board",
                                "physician_visit",
                                "surgery",
                                "diagnostic_imaging",
                                "physiotherapy",
                                "prescription_drugs",
                                "accidental_death_and_dismemberment",
                                "dental_treatment",
                                "ambulance"
                            ]
                        }
                    },
                    "required": ["bill_amount", "benefit_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "exclusion_checker_agent",
                "description": "Checks if the scenario falls under exclusions like intoxication, acts of war, cosmetic surgery, non-school sports.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scenario_details": {
                            "type": "string",
                            "description": "Detailed description of how the injury/incident happened (e.g., occurred during an unsupervised soccer game, injured while intoxicated)."
                        }
                    },
                    "required": ["scenario_details"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "grievance_agent",
                "description": "Helps the user appeal a denied claim or handle grievances.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Details about the denial, timelines, or grievance queries."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "checklist_agent",
                "description": "Lists what documents and claim forms are required to submit proof of loss.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "General query about notice of claim or proof of loss documents."
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    prompt = f"""
    You are the Router Agent. You inspect user queries and route them to the most appropriate specialized agent tool.
    Extract the necessary arguments for the selected tool if they are present in the user query.
    
    User Query: "{query}"
    """
    
    try:
        # Query OpenRouter with the list of tools. Tool choice is auto.
        response = query_llm(prompt, tools=tools, tool_choice="auto")
        
        if isinstance(response, dict) and 'tool_calls' in response:
            tool_call = response['tool_calls'][0]
            agent_name = tool_call.get('function', {}).get('name', 'policy_rag_agent')
            arguments = tool_call.get('function', {}).get('arguments', '{}')
            
            if isinstance(arguments, str):
                parsed_args = json.loads(arguments)
            else:
                parsed_args = arguments
                
            print(f"Router Agent matched Tool: {agent_name} with Args: {parsed_args}")
            return agent_name, parsed_args
            
        print(f"Router Agent fallback (no tool call): {response}")
        return "policy_rag_agent", {"query": query}
        
    except Exception as e:
        print(f"Error in Router Agent tool routing: {e}")
        return "policy_rag_agent", {"query": query}
