# AI Agent using LangGraph

https://www.langchain.com/langgraph

https://docs.langchain.com/oss/python/deepagents/overview


## build a minimal AI Agent using LangGraph (modern & cleaner than classic LangChain agents).

Goal:

✅ Local only (no cloud)
✅ Uses Ollama embeddings + generation
✅ Uses Qdrant as memory / knowledge
✅ Demonstrates real agent behavior (tool usage)
✅ Extremely small & understandable

Pre-requisites
✔ Qdrant running
✔ Ollama running
✔ Documents ingested
✔ MCP server working

## Architecture:

Minimum Agent

User Question → Agent → Decides to use Qdrant Tool → Retrieves Context → Generates Answer

'''shell
LangGraph Agent
    ↓
Qdrant Search Tool
    ↓
Ollama LLM
'''

✅ Step 1 — Install Dependencies

Run once:

pip install langgraph langchain langchain-community qdrant-client ollama

✅ Step 2 — Create Agent Script

Create new file:

agent_qdrant_demo.py


✅ Step 3 — Run Agent
python agent_qdrant_demo.py

Example:

💬 Ask something: What is GitOps?

You will see:

🔎 Searching Qdrant...
🧠 Generating Answer with Ollama...

✅ FINAL ANSWER:

Based on the context provided:

GitOps is a set of automated delivery processes that uses software tools to ensure the desired state of the target deployment environments always matches the described states in Git repositories.

Key points from the context:

1.  **Git as the Source of Truth:** Git repositories contain the desired state (Kubernetes manifests) for applications.
2.  **Automation:** Tools (like Argo CD) monitor the Git repositories and automatically apply changes to the Kubernetes clusters to match the desired state defined in Git.
3.  **Declarative Manifests:** The desired state is defined using declarative Kubernetes manifests stored in Git.

Essentially, GitOps treats Git as the single source of truth for both application configuration and deployment strategy, leveraging automation to achieve continuous delivery and deployment.

✅ That is an actual agent workflow, not just a script.

We created:

✔ Explicit state (memory object)
✔ Tool node (Qdrant search)
✔ Reasoning node (LLM)
✔ Graph orchestration (LangGraph)

This is how production agents are designed.

---

$ python agent_qdrant_demo.py

💬 Ask something: What is GitOps?

🔎 Searching Qdrant...

🧠 Generating Answer with Ollama...

✅ FINAL ANSWER:

Based on the context provided:

GitOps is a set of automated delivery processes that uses software tools to ensure the desired state of the target deployment environments always matches the described states in Git repositories.

Key points from the context:

1.  **Git as the Source of Truth:** Git repositories contain the desired state (Kubernetes manifests) for applications.
2.  **Automation:** Tools (like Argo CD) monitor the Git repositories and automatically apply changes to the Kubernetes clusters to match the desired state defined in Git.
3.  **Declarative Manifests:** The desired state is defined using declarative Kubernetes manifests stored in Git.

Essentially, GitOps treats Git as the single source of truth for both application configuration and deployment strategy, leveraging automation to achieve continuous delivery and deployment.

