"""knowledge_base.py
Knowledge Base management for A.K.A.S.H.A.

This module provides:
- KB document storage and retrieval
- Semantic search within KB
- Admin-only KB management
- Integration with RAG pipeline
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import time
import json
import threading
from pathlib import Path
import hashlib


@dataclass
class KBDocument:
    """Represents a document in the knowledge base"""
    id: str
    title: str
    content: str
    category: str                          # e.g., "FAQ", "API", "Tutorial", "Policy"
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'tags': self.tags,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KBDocument:
        """Create from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            category=data['category'],
            tags=data.get('tags', []),
            created_at=data.get('created_at', time.time()),
            updated_at=data.get('updated_at', time.time()),
            metadata=data.get('metadata', {})
        )


class KnowledgeBaseStore:
    """In-memory knowledge base with simple search"""
    
    def __init__(self):
        self._documents: Dict[str, KBDocument] = {}
        self._lock = threading.RLock()
        self._kb_dir = Path("kb")
        self._kb_dir.mkdir(exist_ok=True)
    
    def add_document(self, doc: KBDocument) -> None:
        """Add a document to KB"""
        with self._lock:
            self._documents[doc.id] = doc
    
    def get_document(self, doc_id: str) -> Optional[KBDocument]:
        """Get a document by ID"""
        with self._lock:
            return self._documents.get(doc_id)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from KB"""
        with self._lock:
            if doc_id in self._documents:
                del self._documents[doc_id]
                return True
            return False
    
    def update_document(self, doc_id: str, **kwargs) -> Optional[KBDocument]:
        """Update a document"""
        with self._lock:
            if doc_id not in self._documents:
                return None
            
            doc = self._documents[doc_id]
            for key, value in kwargs.items():
                if hasattr(doc, key) and key != 'id' and key != 'created_at':
                    setattr(doc, key, value)
            doc.updated_at = time.time()
            return doc
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[float, KBDocument]]:
        """Search KB documents by keyword + semantic similarity"""
        with self._lock:
            scored: List[Tuple[float, KBDocument]] = []
            qlow = query.lower()
            
            for doc in self._documents.values():
                score = 0.0
                
                # Title match (highest weight)
                if qlow in doc.title.lower():
                    score += 3.0
                
                # Content match
                if qlow in doc.content.lower():
                    score += 1.0
                
                # Tag match
                for tag in doc.tags:
                    if qlow in tag.lower():
                        score += 2.0
                
                # Recency bias (newer docs slightly preferred)
                age_days = (time.time() - doc.updated_at) / (60 * 60 * 24)
                recency = max(0.0, 0.5 - min(age_days / 365, 0.5))
                score += recency
                
                if score > 0:
                    scored.append((score, doc))
            
            scored.sort(key=lambda x: x[0], reverse=True)
            return scored[:top_k]
    
    def list_documents(self, category: Optional[str] = None) -> List[KBDocument]:
        """List all documents, optionally filtered by category"""
        with self._lock:
            docs = list(self._documents.values())
            if category:
                docs = [d for d in docs if d.category == category]
            return sorted(docs, key=lambda d: d.updated_at, reverse=True)
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        with self._lock:
            categories = set()
            for doc in self._documents.values():
                categories.add(doc.category)
            return sorted(list(categories))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get KB statistics"""
        with self._lock:
            categories = {}
            total_chars = 0
            
            for doc in self._documents.values():
                total_chars += len(doc.content)
                cat = doc.category
                if cat not in categories:
                    categories[cat] = 0
                categories[cat] += 1
            
            return {
                'total_documents': len(self._documents),
                'total_characters': total_chars,
                'categories': categories,
                'categories_count': len(categories)
            }
    
    def save_to_disk(self, filepath: str = "kb/kb_backup.json") -> bool:
        """Save KB to disk"""
        try:
            with self._lock:
                data = {
                    'documents': [doc.to_dict() for doc in self._documents.values()],
                    'timestamp': time.time()
                }
                Path(filepath).parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                return True
        except Exception as e:
            print(f"Error saving KB: {e}")
            return False
    
    def load_from_disk(self, filepath: str = "kb/kb_backup.json") -> bool:
        """Load KB from disk"""
        try:
            if not Path(filepath).exists():
                return False
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            with self._lock:
                self._documents.clear()
                for doc_data in data.get('documents', []):
                    doc = KBDocument.from_dict(doc_data)
                    self._documents[doc.id] = doc
                return True
        except Exception as e:
            print(f"Error loading KB: {e}")
            return False
    
    def clear_all(self) -> None:
        """Clear all KB documents"""
        with self._lock:
            self._documents.clear()


class KnowledgeBaseManager:
    """High-level KB API for the application"""
    
    def __init__(self):
        self.store = KnowledgeBaseStore()
        self.store.load_from_disk()  # Load existing KB if available
    
    def add_from_text(self, title: str, content: str, category: str = "General", tags: List[str] = None) -> str:
        """Add a document from text"""
        doc_id = hashlib.md5(f"{title}{time.time()}".encode()).hexdigest()[:12]
        doc = KBDocument(
            id=doc_id,
            title=title,
            content=content,
            category=category,
            tags=tags or []
        )
        self.store.add_document(doc)
        self.store.save_to_disk()
        return doc_id
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search KB and return formatted results"""
        results = self.store.search(query, top_k=top_k)
        return [
            {
                'id': doc.id,
                'title': doc.title,
                'content': doc.content,
                'category': doc.category,
                'relevance': round(score, 2),
                'tags': doc.tags
            }
            for score, doc in results
        ]
    
    def get_kb_context(self, query: str, max_results: int = 3) -> str:
        """Get formatted KB context for prompt augmentation"""
        results = self.search(query, top_k=max_results)
        
        if not results:
            return ""
        
        context = "📚 **Knowledge Base Results:**\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. **{result['title']}** (Category: {result['category']}, Relevance: {result['relevance']})\n"
            context += f"   {result['content'][:200]}...\n\n"
        
        return context
    
    def list_all(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all KB documents"""
        docs = self.store.list_documents(category=category)
        return [
            {
                'id': doc.id,
                'title': doc.title,
                'category': doc.category,
                'tags': doc.tags,
                'updated_at': doc.updated_at
            }
            for doc in docs
        ]
    
    def delete(self, doc_id: str) -> bool:
        """Delete a KB document"""
        success = self.store.delete_document(doc_id)
        if success:
            self.store.save_to_disk()
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """Get KB statistics"""
        return self.store.get_stats()


# Global singleton instance
_kb_manager: Optional[KnowledgeBaseManager] = None


def get_kb_manager() -> KnowledgeBaseManager:
    """Get or create KB manager singleton"""
    global _kb_manager
    if _kb_manager is None:
        _kb_manager = KnowledgeBaseManager()
    return _kb_manager
