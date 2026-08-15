"""
Query Neo4j Graph using RAG-style pipeline

Prerequisites:
  - pip install neo4j openai
  - Neo4j running with ingested data
"""

import os
from neo4j import GraphDatabase
from openai import OpenAI

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "admin123"

LITELLM_MASTER_URL = os.getenv("LITELLM_MASTER_URL", "http://localhost:4000")


def extract_entities(client: OpenAI, query: str):
    """
    Extract entities from user query
    """
    prompt = f"""
    Extract key technical entities from the query.
    Return only a comma-separated list.

    Query: {query}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    entities = response.choices[0].message.content.strip()
    return [e.strip() for e in entities.split(",") if e.strip()]


def query_graph(tx, entities):
    """
    Query Neo4j for documents related to entities
    """
    results = []

    for entity in entities:
        records = tx.run(
            """
            MATCH (d:Document)-[:MENTIONS]->(e:Entity {name: $entity})
            OPTIONAL MATCH (e)-[:RELATED_TO]-(related:Entity)
            RETURN d.text AS document,
                   e.name AS entity,
                   collect(DISTINCT related.name) AS related_entities
            LIMIT 5
            """,
            entity=entity,
        )

        for record in records:
            results.append({
                "document": record["document"],
                "entity": record["entity"],
                "related": record["related_entities"],
            })

    return results


def build_context(graph_results):
    """
    Convert graph results into LLM-friendly context
    """
    context = ""

    for r in graph_results:
        context += f"""
Document: {r['document']}
Entity: {r['entity']}
Related: {", ".join(r['related'])}
---
"""

    return context


def generate_answer(client: OpenAI, query: str, context: str):
    """
    Generate final answer using LLM
    """
    prompt = f"""
    You are an AI knowledge assistant.

    Use the context below to answer the query.

    Context:
    {context}

    Query:
    {query}

    Answer clearly and concisely.
    """

    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content


def main():
    litellm_master_key = os.getenv("LITELLM_MASTER_KEY")
    if not litellm_master_key:
        raise RuntimeError("LITELLM_MASTER_KEY is not set.")

    openai_client = OpenAI(api_key=litellm_master_key, base_url=LITELLM_MASTER_URL)

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
    )

    query = input("Enter your query: ")

    # Step 1: Extract entities from query
    entities = extract_entities(openai_client, query)
    print(f"\nExtracted Entities: {entities}")

    # Step 2: Query Neo4j
    with driver.session() as session:
        graph_results = session.execute_read(query_graph, entities)

    print(f"\nGraph Results: {graph_results}")

    # Step 3: Build context
    context = build_context(graph_results)

    # Step 4: Generate answer
    answer = generate_answer(openai_client, query, context)

    print("\n Answer:\n")
    print(answer)

    driver.close()


if __name__ == "__main__":
    main()