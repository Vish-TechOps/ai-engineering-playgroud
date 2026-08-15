"""
Ingest sample documents into Neo4j (Graph DB)

Prerequisites:
  - pip install neo4j openai
  - Set LITELLM_MASTER_URL and LITELLM_MASTER_KEY
  - Run Neo4j locally or remote
"""

import os
import uuid
from neo4j import GraphDatabase
from openai import OpenAI

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "admin123"

LITELLM_MASTER_URL = os.getenv("LITELLM_MASTER_URL", "http://localhost:4000")

# Same documents as your Qdrant pipeline
DOCUMENTS = [
    "Context engineering is everything in LLM",
    "Agent Skills are a set of instructions packaged as a simple folder that teaches Claude how to handle specific tasks or workflows",
    "Qdrant is a high performance vector database",
    "Neo4j is a graph database used for relationships",
    "RAG means Retrieval Augmented Generation.",
]


def extract_entities(client: OpenAI, text: str):
    """
    Use LLM to extract entities from text.
    Keep it simple: return list of keywords.
    """
    prompt = f"""
    Extract key technical entities from the text.
    Return only a comma-separated list.

    Text: {text}
    """

    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    entities = response.choices[0].message.content.strip()
    return [e.strip() for e in entities.split(",") if e.strip()]


def create_constraints(tx):
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")


def ingest_document(tx, doc_id, text, entities):
    # Create Document node
    tx.run(
        """
        MERGE (d:Document {id: $doc_id})
        SET d.text = $text
        """,
        doc_id=doc_id,
        text=text,
    )

    # Create entities and relationships
    for entity in entities:
        tx.run(
            """
            MERGE (e:Entity {name: $entity})
            WITH e
            MATCH (d:Document {id: $doc_id})
            MERGE (d)-[:MENTIONS]->(e)
            """,
            entity=entity,
            doc_id=doc_id,
        )

    # Create relationships between entities (co-occurrence)
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            tx.run(
                """
                MERGE (e1:Entity {name: $e1})
                MERGE (e2:Entity {name: $e2})
                MERGE (e1)-[:RELATED_TO]->(e2)
                """,
                e1=entities[i],
                e2=entities[j],
            )


def main():
    litellm_master_key = os.getenv("LITELLM_MASTER_KEY")
    if not litellm_master_key:
        raise RuntimeError("LITELLM_MASTER_KEY is not set.")

    openai_client = OpenAI(api_key=litellm_master_key, base_url=LITELLM_MASTER_URL)

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
    )

    with driver.session() as session:
        session.execute_write(create_constraints)

        for doc in DOCUMENTS:
            doc_id = str(uuid.uuid4())

            # Step 1: Extract entities (LLM-based)
            entities = extract_entities(openai_client, doc)

            print(f"\nDoc: {doc}")
            print(f"Entities: {entities}")

            # Step 2: Insert into Neo4j
            session.execute_write(ingest_document, doc_id, doc, entities)

    driver.close()
    print("\nDocuments ingested into Neo4j ✅")


if __name__ == "__main__":
    main()