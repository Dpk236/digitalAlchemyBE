import os
import json
import fitz
import sys
from pathlib import Path
# Add parent directory to path to find store module
sys.path.append(str(Path(__file__).parent.parent))
import store.env_loader
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from Services.Embedding.sentence_transform_embeddings import SentenceTransformerEmbeddings

def ingest_pdfs():
    # Configuration
    PDF_FOLDER = os.path.join(os.path.dirname(__file__), "pdf")
    IMAGE_CACHE = os.path.join(os.path.dirname(__file__), "pdf_pages_cache")
    COLLECTION_NAME = "ask_doubt_rag2"
    
    os.makedirs(IMAGE_CACHE, exist_ok=True)
    embeddings_model = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")
    documents = []

    # Loop through PDFs
    for file in os.listdir(PDF_FOLDER):
        if file.lower().endswith(".pdf"):
            path = os.path.join(PDF_FOLDER, file)
            print(f"📸 Converting {file} to images...")
            
            # Open PDF with PyMuPDF
            doc_pdf = fitz.open(path)
            
            for i, page in enumerate(doc_pdf):
                img_name = f"{file}_p{i+1}.jpg"
                img_path = os.path.join(IMAGE_CACHE, img_name)
                
                # Render page to image (approx 150 DPI)
                # default is 72 dpi, so zoom=2 gives ~144 dpi
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
                pix.save(img_path)
                
                # We store the image path in a JSON string for our custom embedder
                content = json.dumps({"image": img_path, "text": f"Source: {file}, Page: {i+1}"})
                doc = Document(page_content=content, metadata={"file": file, "page": i+1})
                documents.append(doc)
            
            doc_pdf.close()

    print(f"📦 Indexing {len(documents)} pages into Qdrant...")
    QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embeddings_model,
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY", None),
        collection_name=COLLECTION_NAME,
        force_recreate=False # Keep existing transcript data
    )
    print("✅ Ingestion complete.")

if __name__ == "__main__":
    print("started")
    ingest_pdfs()