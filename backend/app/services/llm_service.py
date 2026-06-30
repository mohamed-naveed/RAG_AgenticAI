import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel(os.getenv("MODEL_NAME", "gemini-2.5-flash"))

def generate_agent_response(system_prompt: str, context: list, query: str) -> str:
    """
    Calls the Gemini LLM with the specific agent's system prompt, retrieved context, and user query.
    """
    
    # Format the context
    context_text = ""
    for idx, chunk in enumerate(context):
        page = chunk.get('page_number', 'Unknown')
        text = chunk.get('text', '')
        context_text += f"\n--- Chunk {idx+1} (Page {page}) ---\n{text}\n"
        
    full_prompt = f"""
{system_prompt}

You must rely PRIMARILY on the provided Context to answer the question.
When providing your answer, you should include citations to the source pages (e.g., "According to Page 3...").
If the answer cannot be found in the context, state clearly that you do not have that information based on the policy provided.

[CONTEXT START]
{context_text}
[CONTEXT END]

[USER QUERY]
{query}
"""
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the response: {e}"
