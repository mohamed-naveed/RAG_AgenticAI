import os
import requests
import json
from dotenv import load_dotenv

# Ensure env vars are loaded before reading GEMINI_API_KEY
load_dotenv(override=True)

def query_llm(prompt: str, system_prompt: str = None, tools: list = None, tool_choice: any = None) -> any:
    """
    Core function that queries the OpenRouter API. Supports optional tools and tool_choice.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("MODEL_NAME", "google/gemini-2.5-flash")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    messages = []
    if system_prompt:
        user_content = f"{system_prompt}\n\n{prompt}"
    else:
        user_content = prompt
    messages.append({"role": "user", "content": user_content})
    
    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 1000,  # Explicitly set max_tokens to avoid high credit check issues
        "temperature": 0.0  # Ensure highly deterministic, factual answers for QA
    }
    
    if tools:
        payload["tools"] = tools
    if tool_choice:
        payload["tool_choice"] = tool_choice
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        message = data['choices'][0]['message']
        
        # If the model chose to call a tool, return the whole message object containing 'tool_calls'
        if 'tool_calls' in message and message['tool_calls']:
            return message
            
        return message.get('content', '')
    except Exception as e:
        try:
            error_detail = response.json().get('error', {}).get('message', str(e))
        except Exception:
            error_detail = str(e)
        return f"An error occurred while generating the response: {error_detail}"

def generate_agent_response(system_prompt: str, context: list, query: str) -> str:
    """
    Calls the OpenRouter API with the agent's system prompt, retrieved context, and query.
    """
    # Format the context
    context_text = ""
    for idx, chunk in enumerate(context):
        page = chunk.get('page_number', 'Unknown')
        text = chunk.get('text', '')
        context_text += f"\n--- Chunk {idx+1} (Page {page}) ---\n{text}\n"
        
    full_prompt = f"""
You must rely PRIMARILY on the provided Context to answer the question.
When providing your answer, you should include citations to the source pages (e.g., "According to Page 3...").
If the answer cannot be found in the context, state clearly that you do not have that information based on the policy provided.

[CONTEXT START]
{context_text}
[CONTEXT END]

[USER QUERY]
{query}
"""
    return query_llm(full_prompt, system_prompt)
