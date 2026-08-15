from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from pypdf import PdfReader
import ollama
import uuid
import os

# -------------------------
# CONFIG
# -------------------------
PDF_FILE = "gitops.pdf"
COLLECTION = "tech_local_docs"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 100     # overlap improves retrieval

# -------------------------
# Connect Qdrant
# -------------------------
client = QdrantClient(url="http://localhost:6333")

# -------------------------
# Create collection if needed
# -------------------------
if COLLECTION not in [c.name for c in client.get_collections().collections]:
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

# -------------------------
# Read PDF
# -------------------------
if not os.path.exists(PDF_FILE):
    raise FileNotFoundError(f"{PDF_FILE} not found in current directory")

reader = PdfReader(PDF_FILE)

full_text = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        full_text += text + "\n"

print(f"Loaded PDF, total characters: {len(full_text)}")

# -------------------------
# Chunking logic
# -------------------------
def chunk_text(text, size, overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks

chunks = chunk_text(full_text, CHUNK_SIZE, CHUNK_OVERLAP)

print(f"Generated {len(chunks)} chunks")

# -------------------------
# Embed + Insert
# -------------------------
points = []

for chunk in chunks:
    embedding = ollama.embeddings(
        model=EMBED_MODEL,
        prompt=chunk
    )["embedding"]

    points.append({
        "id": str(uuid.uuid4()),
        "vector": embedding,
        "payload": {
            "text": chunk,
            "source": PDF_FILE
        }
    })

# Batch upload (much faster)
client.upsert(
    collection_name=COLLECTION,
    points=points
)

print("PDF successfully ingested into Qdrant 🚀")