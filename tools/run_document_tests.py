#!/usr/bin/env python3
"""Headless document ingestion tests for `app.process_document`.

Usage:
    python tools/run_document_tests.py

This script imports `app.process_document` and tests it against a few
sample files placed in `tools/test_samples` and `assets`.
"""
import sys
from pathlib import Path
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    import app
except Exception as e:
    print("Failed to import app.py:", e)
    traceback.print_exc()
    sys.exit(2)

class UploadedMock:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data
    def getvalue(self):
        return self._data

samples = [
    ("text", ROOT / "tools" / "test_samples" / "sample_text.txt"),
    ("pdf", ROOT / "tools" / "test_samples" / "sample_pdf_like.pdf"),
    ("image", ROOT / "assets" / "user_avatar.png"),
]

print("Running document ingestion tests against sample files...")
all_ok = True
for kind, p in samples:
    if not p.exists():
        print(f"SKIP missing sample: {p}")
        continue
    data = p.read_bytes()
    uf = UploadedMock(p.name, data)
    print(f"\n=== Testing {p.name} ({kind}) - {len(data)} bytes ===")
    try:
        res = app.process_document(uf)
    except Exception as e:
        print(f"process_document raised an exception: {e}")
        traceback.print_exc()
        all_ok = False
        continue
    if res is None:
        print("-> process_document returned None")
        all_ok = False
        continue
    # Print summary
    if isinstance(res, dict):
        t = res.get("type")
        chunks = res.get("chunks") or []
        text_content = res.get("text_content") or []
        print(f"-> type={t}, chunks={len(chunks)}, text_content_items={len(text_content)}")
        if text_content:
            sample_text = text_content[0][:300].replace("\n", " ")
            print("Sample text snippet:", sample_text)
        else:
            # If chunks exist but no text_content, try printing first chunk page_content
            if chunks:
                try:
                    pc = getattr(chunks[0], 'page_content', '')
                    print("Chunk snippet:", (pc or '')[:300].replace("\n"," "))
                except Exception:
                    pass
            else:
                print("-> No textual content found in result")
                all_ok = False
    else:
        print("-> Unexpected return type:", type(res))
        all_ok = False

if all_ok:
    print("\nALL TESTS PASSED")
    sys.exit(0)
else:
    print("\nSOME TESTS FAILED")
    sys.exit(1)
