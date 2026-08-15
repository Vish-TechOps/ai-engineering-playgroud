# Neo4j: Graphs for Everyone

### Neo4j is the world’s leading Graph Database. It is a high performance graph store with all the features expected of a mature and robust database, like a friendly query language and ACID transactions. The programmer works with a flexible network structure of nodes and relationships rather than static tables — yet enjoys all the benefits of enterprise-quality database. For many applications, Neo4j offers orders of magnitude performance benefits compared to relational DBs.

https://github.com/neo4j/neo4j

### Neo4j Desktop

https://neo4j.com/download/

### Core Neo4j concepts:

✅ Nodes
✅ Relationships
✅ Properties
✅ Basic Queries
✅ Graph Thinking

STEPS

Step 1 — Open Neo4j Desktop
Launch Neo4j Desktop 2.1.2
New Project → (name anything)

Step 2 — Create Local Database
Add → Local DBMS

Step 3 — Start Database
Click Start
Wait until status shows: Active

Step 4 — Open Neo4j Browser
http://localhost:7474
Login
Username → neo4j
Password → a*****123

Your First Graph Example (People & Skills)

We’ll model:

✔ People
✔ Skills
✔ Who knows what

This teaches the essence of graph DBs.

Step 5 — Create Nodes
Paste this exact query in Neo4j Browser:
CREATE 
  (vish:Person {name: "Vish", role: "DevOps Engineer"}),
  (alice:Person {name: "Alice", role: "Platform Engineer"}),
  (bob:Person {name: "Bob", role: "SRE"});

Click ▶ Run
✅ You created 3 nodes

Neo4j concept:
(Person) = Node
{name:"Vish"} = Properties

Step 6 — Create Skill Nodes
CREATE
  (k8s:Skill {name: "Kubernetes"}),
  (gitops:Skill {name: "GitOps"}),
  (python:Skill {name: "Python"});

Run ▶

✅ Now graph has skill nodes

Step 7 — Create Relationships (Most Important Part)
MATCH (vish:Person {name: "Vish"}), (k8s:Skill {name: "Kubernetes"})
CREATE (vish)-[:KNOWS]->(k8s);

MATCH (alice:Person {name: "Alice"}), (gitops:Skill {name: "GitOps"})
CREATE (alice)-[:KNOWS]->(gitops);

MATCH (bob:Person {name: "Bob"}), (python:Skill {name: "Python"})
CREATE (bob)-[:KNOWS]->(python);

Run ▶

✅ You just created edges in the graph

Step 8 — Visualize Graph
Run: 
MATCH (n) RETURN n;

🎉 You will SEE the graph visually.

This is why Neo4j is powerful — relationships are first-class citizens.

----
### Basic Queries

Find all persons
MATCH (p:Person) RETURN p;

Find all skills
MATCH (s:Skill) RETURN s;

Who Knows what?
MATCH (p:Person)-[:KNOWS]->(s:Skill)
RETURN p.name, s.name;

Find person who knows kubernetes?
MATCH (p:Person)-[:KNOWS]->(s:Skill)
RETURN p.name, s.name;

Optional — Delete everything (reset DB)
MATCH (n) DETACH DELETE n;

🧠 What you just learned (core Neo4j fundamentals)

✔ Nodes → entities (Person, Skill)
✔ Relationships → connections (KNOWS)
✔ Properties → data fields
✔ Cypher Query Language → SQL equivalent
✔ Graph Visualization → huge advantage

---







