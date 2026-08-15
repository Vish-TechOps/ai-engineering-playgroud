from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from qdrant_client import QdrantClient
import ollama


# ---- STATE DEFINITION (Agent Memory) ----

class AgentState(TypedDict):
    question: str
    context: List[str]
    answer: str


# ---- LOCAL SERVICES ----

qdrant = QdrantClient(url="http://localhost:6333")


# ---- TOOL: QDRANT SEARCH ----

def search_qdrant(state: AgentState) -> AgentState:
    print("\n🔎 Searching Qdrant...")

    embedding = ollama.embeddings(
        model="nomic-embed-text",
        prompt=state["question"]
    )["embedding"]

    hits = qdrant.query_points(
        collection_name="tech_local_docs",   # <-- your PDF collection
        query=embedding,
        limit=3
    )

    context = [hit.payload["text"] for hit in hits.points]

    return {
        **state,
        "context": context
    }


# ---- LLM NODE ----

def generate_answer(state: AgentState) -> AgentState:
    print("\n🧠 Generating Answer with Ollama...")

    combined_context = "\n".join(state["context"])

    prompt = f"""
Answer the question using the context below.

Context:
{combined_context}

Question:
{state['question']}
"""

    response = ollama.chat(
        model="deepseek-r1",    # any local model you have
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        **state,
        "answer": response["message"]["content"]
    }


# ---- GRAPH DEFINITION ----

graph = StateGraph(AgentState)

graph.add_node("search", search_qdrant)
graph.add_node("llm", generate_answer)

graph.set_entry_point("search")

graph.add_edge("search", "llm")
graph.add_edge("llm", END)

agent = graph.compile()


# ---- RUN AGENT ----

if __name__ == "__main__":
    question = input("\n💬 Ask something: ")

    result = agent.invoke({
        "question": question,
        "context": [],
        "answer": ""
    })

    print("\n✅ FINAL ANSWER:\n")
    print(result["answer"])