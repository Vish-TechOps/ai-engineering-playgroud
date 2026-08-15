from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from neo4j import GraphDatabase
from openai import OpenAI
import uuid
import os

# ---------------- CONFIG ----------------

QDRANT_COLLECTION = "hybrid_docs"
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password"   # change to yours

# -----------------------------------------

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

qdrant = QdrantClient(url="http://localhost:6333")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def simple_entity_extraction(text):
    """VERY naive entity extraction (for learning only)"""
    entities = []
    if "Kubernetes" in text:
        entities.append("Kubernetes")
    if "GitOps" in text:
        entities.append("GitOps")
    if "Neo4j" in text:
        entities.append("Neo4j")
    if "Qdrant" in text:
        entities.append("Qdrant")
    return entities

def upsert_graph(tx, entities):
    for ent in entities:
        tx.run("MERGE (:Concept {name: $name})", name=ent)

    if len(entities) >= 2:
        tx.run(
            """
            MATCH (a:Concept {name:$a}), (b:Concept {name:$b})
            MERGE (a)-[:RELATED_TO]->(b)
            """,
            a=entities[0],
            b=entities[1],
        )

with open("sample_docs.txt", "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

if not lines:
    raise ValueError("No input data found in sample_docs.txt")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set. Please set it before running ingest.")


def get_embedding(text: str):
    response = openai_client.embeddings.create(
        model=OPENAI_EMBED_MODEL,
        input=text,
    )
    return response.data[0].embedding


first_vector = get_embedding(lines[0])
vector_size = len(first_vector)

# Create collection to match OpenAI embedding dimensions
qdrant.recreate_collection(
    collection_name=QDRANT_COLLECTION,
    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
)

points = []

with driver.session() as session:
    for idx, chunk in enumerate(lines):
        emb = first_vector if idx == 0 else get_embedding(chunk)
        point_id = str(uuid.uuid4())

        points.append(
            PointStruct(
                id=point_id,
                vector=emb,
                payload={"text": chunk},
            )
        )

        entities = simple_entity_extraction(chunk)
        session.write_transaction(upsert_graph, entities)

qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)

print("✅ Hybrid ingest complete")