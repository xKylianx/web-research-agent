"""
Agent de recherche web avec rapport sourcé·´ - v2 avec search_web intégré.

Architecture LangGraph:
  rewrite_query → search_web → fetch_content → dedup_and_rank → synthesize_report → END
"""

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

from .search import search_web


class AgentState(BaseModel):
    """State partagé entre les noeuds du graphe."""
    query: str
    rewritten_queries: list[str] = []
    raw_results: list[dict] = []
    parsed_pages: list[dict] = []
    ranked_sources: list[dict] = []
    report_markdown: str = ""
    report_sources: list[dict] = []
    error: str | None = None


def rewrite_query(state: AgentState) -> AgentState:
    """
    Clarifie et décompose la query en plusieurs requê·´tes de recherche.
    """
    # Version simple: une seule query
    state.rewritten_queries = [state.query]
    return state


def search_web_node(state: AgentState) -> AgentState:
    """
    Noeud de recherche web: appelle search_web pour chaque rewritten query.
    """
    all_results = []
    for query in state.rewritten_queries:
        try:
            results = search_web(query, max_results=10)
            all_results.extend(results)
        except Exception as e:
            state.error = f"Erreur search_web pour '{query}': {e}"
    
    # D éduplication simple par URL
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)
    
    state.raw_results = unique_results
    return state


def fetch_content(state: AgentState) -> AgentState:
    """Fetch et parse le contenu HTML de chaque résultat."""
    # TODO: impl émenter avec httpx + BeautifulSoup
    state.parsed_pages = []
    return state


def dedup_and_rank(state: AgentState) -> AgentState:
    """D éduplication s émantique et scoring des sources."""
    # TODO: impl émenter avec sentence-transformers
    state.ranked_sources = []
    return state


def synthesize_report(state: AgentState) -> AgentState:
    """G én ère le rapport Markdown sourcé·´."""
    # TODO: impl émenter avec LLM
    state.report_markdown = "# Rapport de recherche\n\n*À·" impl émenter*\n"
    state.report_sources = []
    return state


def build_graph() -> StateGraph:
    """Construit le graphe LangGraph de l'agent."""
    graph = StateGraph(AgentState)
    
    graph.add_node("rewrite_query", rewrite_query)
    graph.add_node("search_web", search_web_node)
    graph.add_node("fetch_content", fetch_content)
    graph.add_node("dedup_and_rank", dedup_and_rank)
    graph.add_node("synthesize_report", synthesize_report)
    
    graph.add_edge(START, "rewrite_query")
    graph.add_edge("rewrite_query", "search_web")
    graph.add_edge("search_web", "fetch_content")
    graph.add_edge("fetch_content", "dedup_and_rank")
    graph.add_edge("dedup_and_rank", "synthesize_report")
    graph.add_edge("synthesize_report", END)
    
    return graph


class ResearchAgent:
    """Agent de recherche web avec rapport sourcé·´."""
    
    def __init__(self):
        self.graph = build_graph().compile()
    
    def research(self, query: str, max_sources: int = 10) -> AgentState:
        """
        Ex écute une recherche web et retourne un rapport sourcé·´.
        
        Args:
            query: La question ou le sujet de recherche.
            max_sources: Nombre maximum de sources à garder après déduplication.
        
        Returns:
            AgentState avec report_markdown et report_sources remplis.
        """
        initial_state = AgentState(query=query)
        final_state = self.graph.invoke(initial_state)
        return final_state


if __name__ == "__main__":
    # Test avec search_web
    from rich.console import Console
    console = Console()
    
    agent = ResearchAgent()
    query = "Quelles sont les derni ères avanc ées en RAG en 2025 ?"
    
    console.print(f"\n[bold blue]Recherche:[/bold blue] {query}")
    result = agent.research(query)
    
    if result.error:
        console.print(f"\n[red]Erreur:[/red] {result.error}")
    
    console.print(f"\n[bold green]Sources trouv ées:[/bold green] {len(result.raw_results)}")
    for i, r in enumerate(result.raw_results[:5], 1):
        console.print(f"\n{i}. [bold]{r['title']}[/bold]")
        console.print(f"   [dim]{r['url']}[/dim]")
        console.print(f"   {r['snippet'][:120]}...")
