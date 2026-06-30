from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base

class Policy(Base):
    __tablename__ = "policies"

    policy_id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(String(255), index=True, nullable=False)
    file_path = Column(String(512), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)

    # Relationship to chunks
    chunks = relationship("PolicyChunk", back_populates="policy", cascade="all, delete-orphan")

class PolicyChunk(Base):
    __tablename__ = "policy_chunks"

    chunk_id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.policy_id"), nullable=False)
    section_name = Column(String(255), nullable=True)
    page_number = Column(Integer, nullable=True)
    chunk_text = Column(Text, nullable=False)

    # Back-reference to the parent policy
    policy = relationship("Policy", back_populates="chunks")

class QueryLog(Base):
    __tablename__ = "query_logs"

    query_id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    agent_used = Column(String(100), nullable=True)
    response = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
