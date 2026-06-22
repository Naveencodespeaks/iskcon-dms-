"""
Search and retrieval endpoints.

This router exposes a `/query` endpoint that allows clients to run a
semantic search against the tenant's knowledge base using the RAG
pipeline.  The endpoint returns the top k results including the
retrieved text and scores.  It can be used to answer customer queries
or provide context to agents.
"""

from __future__ import annotations

from typing import List, Tuple, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status

from ...auth.dependencies import get_current_tenant_id
from ...rbac.dependencies import permission_required
from ...services.rag_service import query_rag

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/query")
async def search_query(
    q: str,
    top_k: int = 5,
    tenant_id = Depends(get_current_tenant_id),
    _: None = permission_required("search:query"),
) -> List[Dict[str, Any]]:
    """Run a semantic search query against the tenant's knowledge base.

    Parameters
    ----------
    q: str
        The free text query to embed and search.
    top_k: int
        Number of results to return (default 5).

    Returns
    -------
    list of dict
        Each result contains ``text``, ``score`` and ``payload`` fields.
    """
    results = query_rag(tenant_id=str(tenant_id), query=q, top_k=top_k)
    response: List[Dict[str, Any]] = []
    for text, score, payload in results:
        response.append({"text": text, "score": score, "payload": payload})
    return response