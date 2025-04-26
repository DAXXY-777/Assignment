import os
from typing_extensions import TypedDict
from tavily import TavilyClient
from langgraph.graph import StateGraph, START, END
from langchain.agents import initialize_agent
from langchain_core.tools.simple import Tool
from langchain_ollama import ChatOllama
from neo4j import GraphDatabase


# 1. Tavily client for crawling
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "key")
tavily = TavilyClient(api_key=TAVILY_API_KEY)  # :contentReference[oaicite:10]{index=10}

# 2. Neo4j driver for KG persistence
NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "pass")
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))  # :contentReference[oaicite:11]{index=11}



# 3. LLM via Ollama (local)
llm = ChatOllama(model="phi4")  # :contentReference[oaicite:13]{index=13}

# 4. LangChain agent for answer drafting
def query_graph(query: str, limit: int = 5) -> str:
    cypher = (
        "MATCH (e:Entity) WHERE toLower(e.name) CONTAINS toLower($q) "
        "WITH e LIMIT $limit "
        "MATCH (e)-[r]->(o) RETURN e.name AS subject, type(r) AS predicate, o.name AS object"
    )
    with neo4j_driver.session() as session:
        recs = session.run(cypher, q=query, limit=limit)
        return "\n".join(
            f"{r['subject']} {r['predicate']} {r['object']}" for r in recs
        )

tools = [
    Tool(
        name="GraphQuery", 
        func=query_graph,
        description="Fetch relevant triples from the Neo4j knowledge graph by keyword"
    )
]
agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description", verbose=True,  handle_parsing_errors=True)  # :contentReference[oaicite:14]{index=14}

# =========================
# Node Definitions
# =========================
class AgentState(TypedDict):
    query: str
    pages: list[dict]
    answer: str

def crawl_node(state: AgentState) -> dict:
    results = tavily.search(state["query"], depth=2)  # :contentReference[oaicite:15]{index=15}
    pages = [{"title": r["title"], "url": r["url"], "content": r["raw_content"]} 
             for r in results["results"]]
    return {"pages": pages}

def parse_node(state: AgentState) -> dict:
    def extract_entities_relations(text: str) -> list[tuple[str,str,str]]:
        # TODO: implement real NER/RE (e.g., spaCy or an LLM call)
        return []
    with neo4j_driver.session() as session:
        for pg in state["pages"]:
            for s, p, o in extract_entities_relations(pg["content"]):
                session.run(
                    "MERGE (a:Entity {name: $s}) "
                    "MERGE (b:Entity {name: $o}) "
                    "MERGE (a)-[:`%s`]->(b)" % p,
                    s=s, o=o
                )
    return {}

def draft_node(state: AgentState) -> dict:
    context = query_graph(state["query"])
    prompt  = f"Use the following context to answer the question:\n{context}\nQuestion: {state['query']}"
    return {"answer": agent.run(prompt)}

# =========================
# Build & Compile Workflow
# =========================
builder = StateGraph(AgentState)  # :contentReference[oaicite:16]{index=16}

builder.add_node("crawl",  crawl_node)
builder.add_node("parse",  parse_node)
builder.add_node("draft",  draft_node)

builder.add_edge(START,   "crawl")  # :contentReference[oaicite:17]{index=17}
builder.add_edge("crawl",  "parse")
builder.add_edge("parse",  "draft")
builder.add_edge("draft",  END)

graph = builder.compile()  # :contentReference[oaicite:18]{index=18}

# =========================
# Main Execution
# =========================
if __name__ == "__main__":
    user_query = input("Enter your research question: ")
    result = graph.invoke({"query": user_query})
    print("\n===== Research-AI Answer =====")
    print(result["answer"])
