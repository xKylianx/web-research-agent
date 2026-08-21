"""
Agent de recherche web avec rapport sourcé·´.

Architecture LangGraph:
  rewrite_query → search_web → fetch_content → dedup_and_rank → synthesize_report → END
"""

from typing import Annotated
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel


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
    
    TODO:
    - Impl émenter le rewriting avec un LLM
    - Gén érer 2-4 requê·´tes enrichies
    """
    # Exemple trivial pour l'instant
    state.rewritten_queries = [state.query]
    return state


def search_web(state: AgentState) -> AgentState:
    """
    Effectue des recherches web pour chaque rewritten query.
    
    TODO:
    - Int égrer Tavily / SerpAPI / Brave Search
    - Stocker title, url, snippet, published_date
    """
    # Placeholder
    state.raw_results = []
    return state


def fetch_content(state: AgentState) -> AgentState:
    """
    Fetch et parse le contenu HTML de chaque résultat.
    
    TODO:
    - httpx + BeautifulSoup
    - Extraire title, body_text, author, published_date
    - G érer les erreurs de fetch
    """
    state.parsed_pages = []
    return state


def dedup_and_rank(state: AgentState) -> AgentState:
    """
    D éduplication s émantique et scoring des sources.
    
    TODO:
    - sentence-transformers pour les embeddings
    - Similarité·´ cosinus + seuil de déduplication
    - Scoring: relevance, quality, recency
    """
    state.ranked_sources = []
    return state


def synthesize_report(state: AgentState) -> AgentState:
    """
    Gén ère le rapport Markdown sourcé·´.
    
    TODO:
    - Prompt LLM avec les sources ranked
    - Gén érer sections thématiques + citations [1], [2], ...
    - Retourner report_markdown et report_sources
    """
    state.report_markdown = "# Rapport de recherche\n\n*À·" impl émenter*\n"
    state.report_sources = []
    return state


def build_graph() -> StateGraph:
    """Construit le graphe LangGraph de l'agent."""
    graph = StateGraph(AgentState)
    
    # Ajout des noeuds
    graph.add_node("rewrite_query", rewrite_query)
    graph.add_node("search_web", search_web)
    graph.add_node("fetch_content", fetch_content)
    graph.add_node("dedup_and_rank", dedup_and_rank)
    graph.add_node("synthesize_report", synthesize_report)
    
    # Connexions
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
        # TODO: passer max_sources dans le state ou config
        final_state = self.graph.invoke(initial_state)
        return final_state


if __name__ == "__main__":
    # Exemple d'usage
    agent = ResearchAgent()
    result = agent.research("Quelles sont les derni ères avanc ées en RAG en 2025 ?")
    print(result.report_markdown)
    print("Sources:", result.report_sources)
