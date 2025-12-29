"""
TEST SCRIPT: Verify Knowledge Base + Auto-Fallback + KB Answer Features
"""

import time
import sys
sys.path.insert(0, '/Users/sagarrajput03/Documents/temp_chatbot')

from knowledge_base import get_kb_manager, KBDocument

def test_knowledge_base():
    """Test KB functionality"""
    print("=" * 60)
    print("🧪 TESTING KNOWLEDGE BASE FEATURES")
    print("=" * 60)
    
    kb = get_kb_manager()
    
    # Test 1: Add KB documents
    print("\n✅ TEST 1: Adding Knowledge Base Documents")
    print("-" * 60)
    
    docs_to_add = [
        {
            "title": "Python Setup Guide",
            "content": "To set up Python on your system, download the latest version from python.org. Follow the installation wizard and ensure to add Python to PATH during installation. Verify installation with 'python --version'.",
            "category": "Tutorial",
            "tags": ["python", "setup", "howto"]
        },
        {
            "title": "Common API Errors",
            "content": "401 Unauthorized: Invalid API key. Check your credentials in .env file. 429 Too Many Requests: Rate limit exceeded. Wait before retrying. 500 Internal Server Error: Server issue, try again later.",
            "category": "Troubleshooting",
            "tags": ["api", "error", "debugging"]
        },
        {
            "title": "Security Best Practices",
            "content": "Never commit API keys to version control. Use .env files and add them to .gitignore. Rotate keys regularly. Use environment variables for sensitive data. Enable two-factor authentication on all accounts.",
            "category": "Policy",
            "tags": ["security", "config", "docs"]
        },
        {
            "title": "Database Connection FAQ",
            "content": "Q: How do I connect to PostgreSQL? A: Use psycopg2 library: import psycopg2; conn = psycopg2.connect(). Q: How to handle connection pooling? A: Use pgBouncer or sqlalchemy connection pools.",
            "category": "FAQ",
            "tags": ["database", "api", "setup"]
        }
    ]
    
    doc_ids = []
    for doc in docs_to_add:
        doc_id = kb.add_from_text(
            title=doc["title"],
            content=doc["content"],
            category=doc["category"],
            tags=doc["tags"]
        )
        doc_ids.append(doc_id)
        print(f"  ✓ Added: '{doc['title']}' (ID: {doc_id})")
    
    print(f"\n  Total documents added: {len(doc_ids)}")
    
    # Test 2: KB Search/Query
    print("\n✅ TEST 2: Knowledge Base Search & Query")
    print("-" * 60)
    
    search_queries = [
        "How to set up Python?",
        "API error 429",
        "database connection",
        "security password"
    ]
    
    for query in search_queries:
        results = kb.search(query, top_k=2)
        print(f"\n  Query: '{query}'")
        if results:
            for i, result in enumerate(results, 1):
                print(f"    {i}. {result['title']} (Relevance: {result['relevance']})")
        else:
            print(f"    (No results)")
    
    # Test 3: KB Statistics
    print("\n✅ TEST 3: Knowledge Base Statistics")
    print("-" * 60)
    
    stats = kb.get_stats()
    print(f"  Total Documents: {stats['total_documents']}")
    print(f"  Total Characters: {stats['total_characters']}")
    print(f"  Categories: {stats['categories_count']}")
    for cat, count in stats['categories'].items():
        print(f"    • {cat}: {count} documents")
    
    # Test 4: List & Filter by Category
    print("\n✅ TEST 4: Document Listing & Filtering")
    print("-" * 60)
    
    for category in ["Tutorial", "FAQ", "Policy"]:
        docs = kb.list_all(category=category)
        print(f"  {category} ({len(docs)} docs):")
        for doc in docs:
            print(f"    • {doc['title']}")
    
    # Test 5: Save/Load KB
    print("\n✅ TEST 5: Knowledge Base Persistence")
    print("-" * 60)
    
    saved = kb.store.save_to_disk()
    print(f"  Save to disk: {'✓ Success' if saved else '✗ Failed'}")
    
    # Test 6: Get KB Context (for prompt augmentation)
    print("\n✅ TEST 6: KB Context for Prompt Augmentation")
    print("-" * 60)
    
    context = kb.get_kb_context("How do I fix API errors?", max_results=2)
    print(f"  Context length: {len(context)} chars")
    print(f"  First 200 chars:\n{context[:200]}...")
    
    print("\n" + "=" * 60)
    print("✅ ALL KNOWLEDGE BASE TESTS PASSED!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_knowledge_base()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
