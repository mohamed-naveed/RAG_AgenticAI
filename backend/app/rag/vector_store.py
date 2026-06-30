import faiss
import numpy as np
from rank_bm25 import BM25Okapi
import pickle
import os

class HybridRetriever:
    def __init__(self, embedding_dimension=384, save_dir="faiss_index"):
        self.embedding_dimension = embedding_dimension
        self.save_dir = save_dir
        self.faiss_index = faiss.IndexFlatL2(embedding_dimension)
        self.bm25 = None
        self.documents = []  # List of dicts with 'text', 'metadata'
        self.tokenized_corpus = []
        
        # Resolve directory to ensure absolute paths relative to backend root
        base_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))
        abs_save_dir = os.path.join(backend_dir, save_dir)
        
        os.makedirs(abs_save_dir, exist_ok=True)
        self.faiss_path = os.path.join(abs_save_dir, "index.faiss")
        self.docs_path = os.path.join(abs_save_dir, "documents.pkl")
        
    def add_documents(self, docs, embeddings):
        """
        Adds documents and their embeddings to the vector store and BM25 index.
        docs: List of dicts, each with 'text' and 'metadata'.
        embeddings: List of numpy arrays or lists (dense embeddings).
        """
        if not docs:
            return
            
        # Add to FAISS
        vectors = np.array(embeddings).astype("float32")
        self.faiss_index.add(vectors)
        
        # Add to local docs list
        self.documents.extend(docs)
        
        # Build/Update BM25
        self.tokenized_corpus = [doc['text'].lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        
    def save(self):
        faiss.write_index(self.faiss_index, self.faiss_path)
        with open(self.docs_path, "wb") as f:
            pickle.dump({"docs": self.documents, "corpus": self.tokenized_corpus}, f)
            
    def load(self):
        if os.path.exists(self.faiss_path) and os.path.exists(self.docs_path):
            self.faiss_index = faiss.read_index(self.faiss_path)
            with open(self.docs_path, "rb") as f:
                data = pickle.load(f)
                self.documents = data["docs"]
                self.tokenized_corpus = data["corpus"]
            if self.tokenized_corpus:
                self.bm25 = BM25Okapi(self.tokenized_corpus)
            return True
        return False
        
    def retrieve(self, query: str, query_embedding, top_k=5, alpha=0.5):
        """
        Retrieves top_k documents using a hybrid score of FAISS (dense) and BM25 (sparse).
        alpha controls the weight: 1.0 is purely dense, 0.0 is purely sparse.
        """
        if not self.documents:
            return []
            
        # Sparse Search (BM25)
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Dense Search (FAISS)
        q_vec = np.array([query_embedding]).astype("float32")
        faiss_distances, faiss_indices = self.faiss_index.search(q_vec, len(self.documents))
        
        # Normalize scores for combination (MinMax)
        def normalize(scores, invert=False):
            if len(scores) == 0: return scores
            min_val, max_val = np.min(scores), np.max(scores)
            if max_val == min_val:
                return np.ones_like(scores) * 0.5
            norm = (scores - min_val) / (max_val - min_val)
            return 1 - norm if invert else norm
            
        # FAISS returns distances (lower is better), so we invert
        dense_scores = np.zeros(len(self.documents))
        for rank, idx in enumerate(faiss_indices[0]):
            if idx != -1:
                # Add a small epsilon to avoid divide by zero if distances are exactly same
                dense_scores[idx] = faiss_distances[0][rank]
                
        # We only consider the distances returned by FAISS for inversion
        # To properly normalize, we need to handle the whole array
        norm_dense = normalize(dense_scores, invert=True)
        norm_sparse = normalize(bm25_scores, invert=False)
        
        # Combine
        hybrid_scores = (alpha * norm_dense) + ((1 - alpha) * norm_sparse)
        
        # Top K
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if hybrid_scores[idx] > 0:  # Ignore completely irrelevant chunks
                res = self.documents[idx].copy()
                res["score"] = float(hybrid_scores[idx])
                results.append(res)
            
        return results

# Singleton instance
retriever_instance = HybridRetriever()
