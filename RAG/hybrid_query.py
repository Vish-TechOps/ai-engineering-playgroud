from qdrant_client import QdrantClient
from neo4j import GraphDatabase
from openai import OpenAI
import argparse
import os


# ---------------- CONFIG ----------------
QDRANT_COLLECTION = "hybrid_docs"
QDRANT_URL = "http://localhost:6333"
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "password")  # change or set env var
# ----------------------------------------


def get_embedding(openai_client: OpenAI, text: str):
    response = openai_client.embeddings.create(
        model=OPENAI_EMBED_MODEL,
        input=text,
    )
    return response.data[0].embedding


def query_qdrant(qdrant: QdrantClient, openai_client: OpenAI, query: str, limit: int = 5):
    query_vector = get_embedding(openai_client, query)
    results = qdrant.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=limit,
    )
    return results


def extract_simple_entities(text: str):
    """Keep this aligned with ingest-time entity extraction."""
    entities = []
    for name in ["Kubernetes", "GitOps", "Neo4j", "Qdrant"]:
        if name.lower() in text.lower():
            entities.append(name)
    return entities


def query_graph_related(driver, entities):
    if not entities:
        return []

    cypher = """
    MATCH (c:Concept)
    WHERE c.name IN $entities
    OPTIONAL MATCH (c)-[:RELATED_TO]->(r:Concept)
    RETURN c.name AS concept, collect(DISTINCT r.name) AS related
    """

    with driver.session() as session:
        records = session.run(cypher, entities=entities)
        return [
            {"concept": rec["concept"], "related": [x for x in rec["related"] if x]}
            for rec in records
        ]


def main():
    parser = argparse.ArgumentParser(description="Hybrid RAG query for Qdrant + Neo4j")
    parser.add_argument("query", type=str, help="User question/query text")
    parser.add_argument("--top-k", type=int, default=5, help="Top K vector results")
    parser.add_argument(
        "--skip-graph",
        action="store_true",
        help="Skip Neo4j concept lookup and only do vector retrieval",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set. Please set it before querying.")

    print("🔎 Initializing OpenAI embedding client...")
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print("🔎 Connecting to Qdrant...")
    qdrant = QdrantClient(url=QDRANT_URL)

    print(f"\nQuery: {args.query}")
    results = query_qdrant(qdrant, openai_client, args.query, limit=args.top_k)

    if not results:
        print("\nNo vector results found. Check ingestion/collection name.")
        return

    print(f"\n📚 Top {len(results)} retrieved chunks from '{QDRANT_COLLECTION}':")
    retrieved_texts = []
    for idx, hit in enumerate(results, start=1):
        text = (hit.payload or {}).get("text", "")
        retrieved_texts.append(text)
        print(f"\n{idx}. score={hit.score:.4f}")
        print(f"   {text}")

    if args.skip_graph:
        return

    print("\n🕸️ Querying Neo4j for related concepts...")
    entities = []
    for t in retrieved_texts:
        entities.extend(extract_simple_entities(t))
    entities = sorted(set(entities))

    if not entities:
        print("No known concepts found in retrieved chunks (Kubernetes/GitOps/Neo4j/Qdrant).")
        return

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        related = query_graph_related(driver, entities)
        driver.close()
    except Exception as e:
        print(f"Neo4j lookup skipped due to connection/query issue: {e}")
        return

    if not related:
        print("No related graph concepts found.")
        return

    print("\n🔗 Graph context:")
    for item in related:
        rel = ", ".join(item["related"]) if item["related"] else "(none)"
        print(f"- {item['concept']} -> {rel}")


if __name__ == "__main__":
    main()
