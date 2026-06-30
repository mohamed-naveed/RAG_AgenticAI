import os
import sys
from dotenv import load_dotenv

# Load env vars before importing DB models
load_dotenv()

from app.database.connection import SessionLocal, engine, Base
from app.database.models import Policy, PolicyChunk
from app.rag.pdf_parser import parse_pdf
from app.rag.chunker import chunk_text
from app.rag.embedder import get_embeddings
from app.rag.vector_store import retriever_instance

def ingest_policy(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"Error: '{pdf_path}' not found. Please place your PDF in the 'backend/data' folder.")
        return

    print(f"Ingesting {pdf_path}...")
    
    try:
        # Create tables just in case they don't exist yet
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database error during table creation: {e}")
        print("Did you update your .env file with the correct DB_PASSWORD?")
        return
    
    # 1. Parse PDF
    print("Parsing PDF...")
    pages = parse_pdf(pdf_path)
    if not pages:
        print("No text found in PDF. Make sure it's a valid text-based PDF.")
        return
        
    # 2. Chunk Text
    print("Chunking text...")
    chunks = chunk_text(pages)
    print(f"Created {len(chunks)} chunks.")
    
    db = SessionLocal()
    try:
        # 3. Create Policy in DB
        filename = os.path.basename(pdf_path)
        
        # Check if already exists
        existing_policy = db.query(Policy).filter(Policy.policy_name == filename).first()
        if existing_policy:
            print(f"Policy {filename} is already in the database. Deleting old chunks...")
            db.delete(existing_policy)
            db.commit()

        policy_record = Policy(policy_name=filename, file_path=pdf_path)
        db.add(policy_record)
        db.commit()
        db.refresh(policy_record)
        
        # 4. Save Chunks to DB
        print("Saving chunks to MySQL...")
        db_chunks = []
        for chunk in chunks:
            db_chunk = PolicyChunk(
                policy_id=policy_record.policy_id,
                page_number=chunk["page_number"],
                chunk_text=chunk["text"]
            )
            db_chunks.append(db_chunk)
        
        db.add_all(db_chunks)
        db.commit()
        
        # 5. Embed and add to Vector Store
        print("Embedding chunks and saving to FAISS... (This might take a minute)")
        texts = [chunk["text"] for chunk in chunks]
        embeddings = get_embeddings(texts)
        
        docs_to_index = []
        for i, chunk in enumerate(chunks):
            docs_to_index.append({
                "text": chunk["text"],
                "page_number": chunk["page_number"],
                "policy_id": policy_record.policy_id
            })
            
        retriever_instance.add_documents(docs_to_index, embeddings)
        retriever_instance.save()
        
        print("\n✅ Ingestion complete! The PDF is now loaded into FAISS and MySQL.")
        print("You can now ask questions using the /api/ask endpoint.")
        
    except Exception as e:
        print(f"Database error during ingestion: {e}")
        print("Did you update your .env file with the correct DB_PASSWORD?")
    finally:
        db.close()

if __name__ == "__main__":
    pdf_location = "data/policy.pdf"
    if len(sys.argv) > 1:
        pdf_location = sys.argv[1]
        
    ingest_policy(pdf_location)
