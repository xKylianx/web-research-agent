"""
Moteurs de recherche web pour l'agent.

Supporte:
- Tavily (dé·´faut)
- SerpAPI (optionnel)
- Brave Search (optionnel)
"""

import os
import httpx
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

SearchProvider = Literal["tavily", "serpapi", "brave"]


def get_provider() -> SearchProvider:
    """Retourne le provider configuré·´ via SEARCH_PROVIDER."""
    provider = os.getenv("SEARCH_PROVIDER", "tavily").lower()
    if provider not in ("tavily", "serpapi", "brave"):
        return "tavily"
    return provider  # type: ignore


def search_tavily(query: str, max_results: int = 10) -> list[dict]:
    """
    Recherche avec Tavily Search API.
    
    Docs: https://docs.tavily.com/docs/api-reference/search
    
    Args:
        query: La requê·´te de recherche.
        max_results: Nombre maximum de résultats à retourner.
    
    Returns:
        Liste de dicts avec: title, url, snippet, published_date (si disponible)
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY non configuré·´e dans l'environnement")
    
    url = "https://api.tavily.com/search"
    payload = {
        "query": query,
        "api_key": api_key,
        "max_results": max_results,
        "search_depth": "advanced",  # plus de résultats, plus pertinent
        "include_answer": False,
        "include_raw_content": False,
    }
    
    with httpx.Client(timeout=15.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
    
    results = []
    for result in data.get("results", []):
        results.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "snippet": result.get("content", ""),
            "published_date": result.get("published_date", None),
            "source": "tavily",
        })
    
    return results


def search_serpapi(query: str, max_results: int = 10) -> list[dict]:
    """
    Recherche avec SerpAPI (Google Search).
    
    Docs: https://serpapi.com/search-api
    
    Args:
        query: La requê·´te de recherche.
        max_results: Nombre maximum de résultats à retourner.
    
    Returns:
        Liste de dicts avec: title, url, snippet, published_date (si disponible)
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY non configuré·´e dans l'environnement")
    
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": max_results,
    }
    
    with httpx.Client(timeout=15.0) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    
    results = []
    for result in data.get("organic_results", [])[:max_results]:
        results.append({
            "title": result.get("title", ""),
            "url": result.get("link", ""),
            "snippet": result.get("snippet", ""),
            "published_date": result.get("date", None),
            "source": "serpapi",
        })
    
    return results


def search_brave(query: str, max_results: int = 10) -> list[dict]:
    """
    Recherche avec Brave Search API.
    
    Docs: https://brave.com/search/api/
    
    Args:
        query: La requê·´te de recherche.
        max_results: Nombre maximum de résultats à retourner.
    
    Returns:
        Liste de dicts avec: title, url, snippet, published_date (si disponible)
    """
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key:
        raise ValueError("BRAVE_SEARCH_API_KEY non configuré·´e dans l'environnement")
    
    url = "https://api.search.brave.com/search/v1/web/search"
    headers = {
        "X-Subscription-Token": api_key,
        "Accept": "application/json",
    }
    params = {
        "q": query,
        "count": max_results,
    }
    
    with httpx.Client(timeout=15.0) as client:
        response = client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
    
    results = []
    for result in data.get("web", {}).get("results", [])[:max_results]:
        results.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "snippet": result.get("description", ""),
            "published_date": result.get("age", None),  # Brave retourne "age" (ex: "2 days ago")
            "source": "brave",
        })
    
    return results


def search_web(query: str, max_results: int = 10, provider: SearchProvider | None = None) -> list[dict]:
    """
    Fonction unifié·´e de recherche web.
    
    Args:
        query: La requê·´te de recherche.
        max_results: Nombre maximum de résultats à retourner.
        provider: Provider à utiliser (dé·´faut: celui configuré·´ dans SEARCH_PROVIDER).
    
    Returns:
        Liste de résultats de recherche.
    """
    if provider is None:
        provider = get_provider()
    
    if provider == "tavily":
        return search_tavily(query, max_results)
    elif provider == "serpapi":
        return search_serpapi(query, max_results)
    elif provider == "brave":
        return search_brave(query, max_results)
    else:
        raise ValueError(f"Provider inconnu: {provider}")


if __name__ == "__main__":
    # Test rapide
    import json
    
    query = "recent advances retrieval augmented generation 2025"
    print(f"Recherche: {query}")
    print(f"Provider: {get_provider()}")
    
    try:
        results = search_web(query, max_results=5)
        print(f"\n{len(results)} résultats trouv ées:\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title']}")
            print(f"   {r['url']}")
            print(f"   {r['snippet'][:150]}...")
            print()
    except ValueError as e:
        print(f"Erreur de configuration: {e}")
        print("\nAssure-toi d'avoir configuré·´ la clé API dans .env:")
        print("  TAVILY_API_KEY=ton_api_key")
