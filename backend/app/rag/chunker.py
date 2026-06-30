from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(pages, chunk_size=800, chunk_overlap=200):
    """
    Chunks the text from pages using RecursiveCharacterTextSplitter.
    Returns a list of chunk dictionaries with metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = []
    for page in pages:
        page_text = page["text"]
        page_number = page["page_number"]
        
        split_texts = text_splitter.split_text(page_text)
        
        for text_chunk in split_texts:
            chunks.append({
                "page_number": page_number,
                "text": text_chunk
            })
            
    return chunks
