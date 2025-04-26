# Deep Research Agentic System

An end-to-end, multi-agent pipeline that:

1. **Crawls** the web for pages matching a research query (via Tavily)  
2. **Parses** pages into structured triples and stores them in a Neo4j knowledge graph  
3. **Drafts** an answer by querying the graph with a LangChain + Ollama agent

Every function in the code maps directly to one step in this workflow.

---

## 📋 Prerequisites

- **Python 3.8+**  
- **Tavily** account & API key  
- **Neo4j** (Desktop or Docker) running at `bolt://localhost:7687`  
- **Ollama** installed & a local model (e.g. `phi4`) pulled and the `ollama` daemon running  
- **Environment variables** set:

  ```bash
  export TAVILY_API_KEY="your_tvly_key"
  export NEO4J_URI="bolt://localhost:7687"
  export NEO4J_USER="neo4j"
  export NEO4J_PASS="your_neo4j_password"
🔧 Installation
Clone or copy this repository to your machine.

Install the Python dependencies:

bash
Copy
Edit
pip install \
  tavily-python \
  neo4j \
  chromadb \
  langchain langchain-core \
  langchain-ollama \
  typing-extensions
Make sure Neo4j is running and you’ve set an initial password for the neo4j user.

Start Ollama (if not already):

bash
Copy
Edit
ollama serve
ollama pull phi4
📂 Code Structure
crawl_node(state)
Fetches web pages matching state["query"] via Tavily and returns a list of pages.

parse_node(state)
Stub for entity/relation extraction: runs extract_entities_relations() on each page’s content and MERGEs triples into Neo4j.

draft_node(state)
Queries the Neo4j graph (GraphQuery tool) for facts matching state["query"], builds a prompt, and invokes the Ollama-powered LangChain agent to generate the final answer.

StateGraph orchestration
Defines the workflow:

sql
Copy
Edit
START → crawl_node → parse_node → draft_node → END
query_graph()
A plain Python function wrapped as a LangChain Tool named GraphQuery, issuing a Cypher query to fetch up to 5 matching triples.

🚀 Usage
Ensure all services (Neo4j, Ollama) are running.

Set your environment variables.

Run the script:

bash
Copy
Edit
python deep_research_agentic_system.py
When prompted:

yaml
Copy
Edit
Enter your research question:
Type any query (e.g. “latest advances in retrieval-augmented generation”) and press Enter.

Watch the multi-agent pipeline execute and display a structured, context-rich answer.

⚙️ Customization
NER / Relation Extraction
Replace the extract_entities_relations() stub in parse_node() with your preferred method (e.g. spaCy, an LLM call, custom regex).

Graph & Tool Extensions
Add more LangChain tools (e.g. semantic-search over ChromaDB) or new LangGraph nodes for additional processing steps.

Model & Prompt Tuning
Swap in a different Ollama model or adjust the prompt templates for specialized domains.

📝 Assignment for kairon.co.in
This project is for the take home assignment.
