# Spé·´cification de l'agent de recherche web

## Vue d'ensemble

Cet agent transforme une question utilisateur en un rapport de recherche web sourcé·´, en suivant un pipeline déterministe orchestré·´ par LangGraph.

## Noeuds du graphe LangGraph

### 1. `rewrite_query`
- **Entré·´e**: `state.query` (string)
- **Sortie**: `state.rewritten_queries` (list[str])
- **Responsabilité·´s**:
  - Clarifier la question (expliciter le contexte implicite)
  - Décomposer en 2-4 sous-questions si néceé·´ssaire
  - Ajouter des termes de recherche pertinents (ex: "2025", "benchmark", "comparatif")
- **Exemple**:
  - Entré·´e: `"Quelles sont les derni ères avanc ées en RAG ?"`
  - Sortie: `[
    "recent advances retrieval augmented generation 2025 2026",
    "RAG improvements vector databases hybrid search 2025",
    "RAG evaluation benchmarks accuracy 2025"
  ]`

### 2. `search_web`
- **Entré·´e**: `state.rewritten_queries`
- **Sortie**: `state.raw_results` (list[dict])
- **Responsabilité·´s**:
  - Appeler un moteur de recherche (Tavily, SerpAPI, ou Brave Search)
  - Limiter à `max_results_per_query` (dé·´faut: 10)
  - Stocker: `title`, `url`, `snippet`, `published_date` (si disponible)
- **Config**:
  - `SEARCH_PROVIDER` (env): `"tavily"` (dé·´faut), `"serpapi"`, `"brave"`
  - `MAX_RESULTS` (dé·´faut: 30)

### 3. `fetch_content`
- **Entré·´e**: `state.raw_results`
- **Sortie**: `state.parsed_pages` (list[dict])
- **Responsabilité·´s**:
  - Fetch HTTP de chaque URL (timeout: 10s)
  - Parser HTML (BeautifulSoup)
  - Extraire: `title`, `body_text` (paragraphes concaté·´né·´s), `author`, `published_date`
  - G érer les erreurs (timeout, 404, contenu non-HTML) → marquer comme `fetch_error`
- **Filtres**:
  - Ignorer les PDF, vidéos, pages avec < 200 caract ères
  - Normaliser le texte (unicode, whitespace)

### 4. `dedup_and_rank`
- **Entré·´e**: `state.parsed_pages`
- **Sortie**: `state.ranked_sources` (list[dict])
- **Responsabilité·´s**:
  - Calculer des embeddings (sentence-transformers, mod èle: `all-MiniLM-L6-v2`)
  - D éduplication s émantique (seuil de similarité·´: 0.85)
  - Scorer chaque source:
    - `relevance_score` (similarité·´ cosinus avec la query)
    - `quality_score` (longueur, présence de date, autorité·´ du domaine)
    - `recency_score` (si date disponible)
  - Trier par `composite_score = 0.5*relevance + 0.3*quality + 0.2*recency`
  - Garder le top `max_sources` (dé·´faut: 10)

### 5. `synthesize_report`
- **Entré·´e**: `state.query`, `state.ranked_sources`
- **Sortie**: `state.report_markdown` (string), `state.report_sources` (list[dict])
- **Responsabilité·´s**:
  - Gén érer un rapport Markdown structur é:
    - Titre H1
    - Résumé exé·´cutif (3-5 lignes)
    - Sections thématiques (H2) avec paragraphes
    - Citations numé·´rot ées [1], [2], etc. li ées aux sources
  - Produire une liste de sources avec:
    - `index`, `title`, `url`, `snippet`, `relevance_score`
- **Prompt LLM** (extrait):
  ```
  Tu es un assistant de recherche. Gén ère un rapport clair et sourcé·´.
  R ègles:
  - Utilise uniquement les sources fournies.
  - Chaque affirmation importante doit avoir une citation [n].
  - Structure en sections thématiques.
  - Style neutre, informatif, sans jargon excessif.
  ```

### 6. `END`
- Retourne `state.report_markdown` et `state.report_sources`

## State Pydantic

```python
from pydantic import BaseModel
from typing import Literal

class AgentState(BaseModel):
    query: str
    rewritten_queries: list[str] = []
    raw_results: list[dict] = []
    parsed_pages: list[dict] = []
    ranked_sources: list[dict] = []
    report_markdown: str = ""
    report_sources: list[dict] = []
    error: str | None = None
```

## Formats d'entré·´e/sortie

### Entré·´e (CLI ou API)
```json
{
  "query": "Quelles sont les derni ères avanc ées en RAG en 2025 ?",
  "max_sources": 10
}
```

### Sortie (rapport)
```json
{
  "markdown": "# Titre\n\nRé·´sum é...\n\n## Section 1\n\nTexte [1][2]...",
  "sources": [
    {
      "index": 1,
      "title": "Article title",
      "url": "https://...",
      "snippet": "...",
      "relevance_score": 0.92
    }
  ]
}
```

## Crit ères de qualité

- **Citations**: Chaque paragraphe important cite ≥1 source.
- **D éduplication**: Aucune source redondante (similarité·´ < 0.85).
- **Fraî·´cheur**: ≥50% des sources datent des 12 derniers mois (si possible).
- **Lisibilité·´**: Rapport ≤1500 mots, sections claires.
- **Robustesse**: G érer les erreurs de fetch sans crash (marquer comme `fetch_error`).

## Variables d'environnement

```bash
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=...
# ou
SERPAPI_API_KEY=...
# ou
BRAVE_SEARCH_API_KEY=...

LLM_PROVIDER=openai  # ou anthropic, ollama
OPENAI_API_KEY=...

MAX_RESULTS=30
MAX_SOURCES=10
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Extensions futures

- [ ] Multi-langues (query rewriting + rapport)
- [ ] Cache des résultats (SQLite ou Redis)
- [ ] Mode "deep research" (plus de sources, plus de temps)
- [ ] Export PDF/HTML
- [ ] Dashboard web (FastAPI + React)
