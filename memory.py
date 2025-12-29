"""memory.py
Scaffold for long-term memory management.

This module exposes a simple MemoryManager API used by the app. It provides
an in-memory fallback implementation so it safely imports even if FAISS or a
remote vector DB is not installed. Later this can be extended to use a
persistent FAISS, Milvus or hosted vector DB.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import time
import threading


@dataclass
class MemoryEntry:
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=lambda: time.time())


class InMemoryStore:
    """Very small in-process memory store used as a safe default.

    The store keeps entries in a list and performs naive similarity by
    optionally using precomputed embeddings (if provided) or simple
    substring matching as a fallback.
    """

    def __init__(self):
        self._entries: List[MemoryEntry] = []
        self._lock = threading.RLock()

    def insert(self, entry: MemoryEntry) -> None:
        with self._lock:
            self._entries.append(entry)

    def query(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        with self._lock:
            # If embeddings are available, a real implementation would compute
            # distances. For this scaffold, fall back to simple substring match
            # and recency ordering.
            scored: List[Tuple[float, MemoryEntry]] = []
            qlow = query.lower()
            for e in self._entries:
                score = 0.0
                if e.embedding:
                    # placeholder: optimistic score for entries with embeddings
                    score += 0.5
                if qlow in e.content.lower():
                    score += 1.0
                # add recency bias
                age = time.time() - e.ts
                score += max(0.0, 0.5 - min(age / (60 * 60 * 24), 0.5))
                scored.append((score, e))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [e for _, e in scored[:top_k]]

    def prune(self, keep_last: int = 1000) -> None:
        with self._lock:
            if len(self._entries) <= keep_last:
                return
            # keep most recent
            self._entries.sort(key=lambda e: e.ts, reverse=True)
            self._entries = self._entries[:keep_last]

    def all_entries(self) -> List[MemoryEntry]:
        with self._lock:
            return list(self._entries)


class MemoryManager:
    """High-level memory manager exposing a stable API for the app.

    Responsibilities:
    - insert memories (optionally compute embeddings externally)
    - query memories with ranking
    - consolidate/prune memories (background job)
    - persist/load (to be implemented in a future extension)
    """

    def __init__(self, store: Optional[InMemoryStore] = None):
        self.store = store or InMemoryStore()

    def insert_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None, embedding: Optional[List[float]] = None) -> MemoryEntry:
        """Insert a new memory entry and return it."""
        mid = f"m_{int(time.time() * 1000)}"
        entry = MemoryEntry(id=mid, content=content, embedding=embedding, metadata=metadata or {})
        self.store.insert(entry)
        return entry

    def query(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        return self.store.query(query, top_k=top_k)

    def consolidate(self) -> None:
        """Placeholder consolidation: in a real system this would summarize
        recent episodic memories into semantic entries and optionally remove
        low-value fragments.
        """
        # No-op scaffold
        return

    def prune(self, keep_last: int = 1000) -> None:
        self.store.prune(keep_last=keep_last)

    # Persistence hooks (to be implemented when FAISS or remote vectorstore is integrated)
    def persist(self, path: str) -> None:
        raise NotImplementedError("Persistence not implemented in scaffold")

    def load(self, path: str) -> None:
        raise NotImplementedError("Load not implemented in scaffold")


__all__ = ["MemoryManager", "MemoryEntry", "InMemoryStore"]
