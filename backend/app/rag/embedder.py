# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer

# Load the model once into memory
_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str) -> list[float]:
    """
    Generates a dense vector embedding for the given text using sentence-transformers.
    """
    # encode returns a numpy array, we convert it to a list
    embedding = _model.encode(text)
    return embedding.tolist()

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generates dense vector embeddings for a list of texts using sentence-transformers.
    """
    embeddings = _model.encode(texts)
    return embeddings.tolist()
