from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import QueryLog
from app.agents import router_agent
from app.rag.vector_store import retriever_instance
from app.rag.embedder import get_embedding
import app.agents.policy_rag_agent as policy_rag_agent
import app.agents.claim_eligibility_agent as claim_eligibility_agent
import app.agents.benefit_calculator_agent as benefit_calculator_agent
import app.agents.exclusion_checker_agent as exclusion_checker_agent
import app.agents.grievance_agent as grievance_agent
import app.agents.checklist_agent as checklist_agent

router = APIRouter()

# Try to load vector store on startup
retriever_instance.load()

class QueryRequest(BaseModel):
    question: str

agent_map = {
    "policy_rag_agent": policy_rag_agent,
    "claim_eligibility_agent": claim_eligibility_agent,
    "benefit_calculator_agent": benefit_calculator_agent,
    "exclusion_checker_agent": exclusion_checker_agent,
    "grievance_agent": grievance_agent,
    "checklist_agent": checklist_agent
}

@router.post("/")
async def ask_question(request: QueryRequest, db: Session = Depends(get_db)):
    query = request.question
    
    # 1. Route query
    routed_agent_name, extracted_args = router_agent.route_query(query)
    
    if routed_agent_name == "Unknown":
        log = QueryLog(
            question=query,
            agent_used="Unknown",
            response="This question is not related to the insurance policy."
        )
        db.add(log)
        db.commit()
        return {
            "agent_used": "Unknown",
            "response": {
                "status": "unrelated",
                "message": "This question is not related to the insurance policy."
            },
            "sources": []
        }
    
    # 2. Retrieve Context
    query_emb = get_embedding(query)
    context_chunks = retriever_instance.retrieve(query, query_emb, top_k=5)
    
    # 3. Generate response using specific agent
    agent_module = agent_map.get(routed_agent_name, policy_rag_agent)
    response_text = agent_module.process(context_chunks, query, arguments=extracted_args)
    
    # 4. Log to DB (save raw text response in SQL)
    log = QueryLog(
        question=query,
        agent_used=routed_agent_name,
        response=response_text
    )
    db.add(log)
    db.commit()
    
    return {
        "agent_used": routed_agent_name,
        "response": response_text,
        "sources": [{"page": c.get("page_number"), "score": c.get("score")} for c in context_chunks]
    }
