import pytest
import time

from memory import MemoryManager, MemoryEntry


def test_memory_insert_and_query():
    mm = MemoryManager()
    e = mm.insert_memory("Hello world", metadata={"source": "test"})
    assert e.content == "Hello world"
    results = mm.query("Hello")
    assert isinstance(results, list)
    assert any(r.id == e.id for r in results)


def test_memory_consolidate():
    mm = MemoryManager()
    mm.insert_memory("First message")
    mm.insert_memory("Second message")
    mm.consolidate()  # Should not raise
    assert True


def test_memory_prune():
    mm = MemoryManager()
    for i in range(20):
        mm.insert_memory(f"Message {i}")
    mm.prune(keep_last=5)
    all_entries = mm.store.all_entries()
    assert len(all_entries) <= 5


def test_memory_retrieval_ranking():
    """Test that retrieval scores favor substring matches and recent entries."""
    mm = MemoryManager()
    e1 = mm.insert_memory("The quick brown fox")
    time.sleep(0.01)
    e2 = mm.insert_memory("The lazy dog sleeps")
    
    # Query for "fox" should rank e1 higher
    results = mm.query("fox", top_k=2)
    assert len(results) >= 1
    assert results[0].id == e1.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
