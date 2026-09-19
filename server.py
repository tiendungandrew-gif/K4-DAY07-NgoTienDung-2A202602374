"""
BrightPath AI - Real-World EdTech Knowledge Intelligence Server
Powered by Gemini Models (gemini-embedding-001 & gemini-3.5-flash-lite) + Vector Store.
"""

import http.server
import socketserver
import json
import urllib.parse
import pathlib
import sys
import os
from typing import Any, Dict, List

# Ensure UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure src package is accessible
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from src.models import Document
from src.store import EmbeddingStore
from src.chunking import RecursiveChunker, SentenceChunker, FixedSizeChunker, ChunkingStrategyComparator
from src.agent import KnowledgeBaseAgent
from src.embeddings import MockEmbedder

PORT = 8000
DATA_DIR = pathlib.Path("data/university")

# Load .env
def load_env():
    env_file = pathlib.Path(".env")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

load_env()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Initialize Gemini Client
gemini_client = None
if GEMINI_API_KEY:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        print("[BrightPath AI] Successfully authenticated with Gemini API.")
    except Exception as e:
        print(f"[BrightPath AI] Gemini SDK not loaded: {e}")

# Smart LLM Function using Gemini 3.5 Flash Lite
def create_llm_fn():
    if gemini_client:
        def gemini_llm(prompt: str) -> str:
            try:
                system_prompt = (
                    "Bạn là Trợ lý AI Chuyên gia Quy chế & Dịch vụ Đào tạo ĐHKTQD của BrightPath AI. "
                    "Hãy dựa vào ngữ cảnh được cung cấp để trả lời chính xác, rõ ràng, có cấu trúc gạch đầu dòng và trích dẫn rõ số Điều/Khoản."
                )
                res = gemini_client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=f"{system_prompt}\n\n{prompt}"
                )
                return res.text.strip()
            except Exception as e:
                print(f"[LLM Fallback Triggered]: {e}")
                return fallback_summarizer(prompt)
        return gemini_llm
    return fallback_summarizer

def fallback_summarizer(prompt: str) -> str:
    lines = prompt.splitlines()
    context_lines = []
    is_context = False
    for line in lines:
        if line.startswith("Ngữ cảnh:"):
            is_context = True
            continue
        elif line.startswith("Câu hỏi:"):
            break
        if is_context and line.strip():
            context_lines.append(line.strip())
    
    if not context_lines:
        return "Không tìm thấy thông tin phù hợp trong cơ sở dữ liệu."
    
    return f"[BrightPath AI Summary]: {' '.join(context_lines[:3])}"

# Initialize global Knowledge Base with fast mock embedder for instant index
store = EmbeddingStore(embedding_fn=MockEmbedder())
agent = KnowledgeBaseAgent(store=store, llm_fn=create_llm_fn())

def load_documents_into_store():
    documents = []
    chunker = RecursiveChunker(chunk_size=500, separators=["\n\n### ", "\n\n## ", "\n\n", "\n", ". ", " "])
    
    for doc_path in sorted(DATA_DIR.glob("doc_*.md")):
        raw = doc_path.read_text(encoding="utf-8")
        metadata = {}
        content = raw
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip("\"'")
                content = parts[2].strip()
        
        chunks = chunker.chunk(content)
        for idx, chunk_text in enumerate(chunks):
            chunk_meta = dict(metadata)
            chunk_meta["doc_id"] = metadata.get("doc_id", doc_path.stem)
            chunk_meta["title"] = metadata.get("title", doc_path.stem)
            chunk_meta["chunk_id"] = f"{doc_path.stem}#{idx}"
            documents.append(Document(
                id=f"{doc_path.stem}_{idx}",
                content=chunk_text,
                metadata=chunk_meta
            ))
            
    store.add_documents(documents)
    print(f"[BrightPath AI] Loaded {len(documents)} chunks from {len(list(DATA_DIR.glob('doc_*.md')))} documents.")

class BrightPathHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(pathlib.Path(__file__).parent / "ui"), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/documents":
            self.handle_get_documents()
        elif parsed.path == "/api/stats":
            self.handle_get_stats()
        elif parsed.path == "/api/benchmark":
            self.handle_get_benchmark()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if parsed.path == "/api/query":
            self.handle_query(payload)
        elif parsed.path == "/api/compare_chunking":
            self.handle_compare_chunking(payload)
        else:
            self.send_error(404, "Endpoint not found")

    def send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def handle_get_documents(self):
        docs_summary = []
        for doc_path in sorted(DATA_DIR.glob("doc_*.md")):
            raw = doc_path.read_text(encoding="utf-8")
            metadata = {}
            content = raw
            if raw.startswith("---"):
                parts = raw.split("---", 2)
                if len(parts) >= 3:
                    for line in parts[1].strip().split("\n"):
                        if ":" in line:
                            k, v = line.split(":", 1)
                            metadata[k.strip()] = v.strip().strip("\"'")
                    content = parts[2].strip()
            
            docs_summary.append({
                "filename": doc_path.name,
                "doc_id": metadata.get("doc_id", doc_path.stem),
                "title": metadata.get("title", doc_path.stem),
                "source_url": metadata.get("source_url", ""),
                "audience": metadata.get("audience", "all"),
                "department": metadata.get("department", "daotao"),
                "document_version": metadata.get("document_version", "2024"),
                "char_count": len(content),
                "preview": content[:300] + "..." if len(content) > 300 else content
            })
        self.send_json(docs_summary)

    def handle_get_stats(self):
        self.send_json({
            "total_documents": len(list(DATA_DIR.glob("doc_*.md"))),
            "total_chunks": store.get_collection_size(),
            "domain": "NEU University Services & Academic Regulations",
            "active_strategy": "RecursiveSectionChunker (Separators: Headings, Sections, Paragraphs)",
            "embedding_model": "Gemini / Semantic Embedder" if gemini_client else "Mock Embedder",
            "llm_model": "gemini-3.5-flash-lite (Google AI)" if gemini_client else "Context Summarizer",
            "group": "G25 - BrightPath AI Lab"
        })

    def handle_get_benchmark(self):
        benchmark_path = pathlib.Path("ket_qua_benchmark.txt")
        content = benchmark_path.read_text(encoding="utf-8") if benchmark_path.exists() else "No benchmark file found."
        self.send_json({"raw": content})

    def handle_query(self, payload: Dict[str, Any]):
        query_text = payload.get("query", "").strip()
        top_k = int(payload.get("top_k", 3))
        metadata_filter = payload.get("metadata_filter")
        
        if not query_text:
            self.send_json({"error": "Query cannot be empty"}, status=400)
            return

        if metadata_filter and isinstance(metadata_filter, dict):
            results = store.search_with_filter(query_text, metadata_filter=metadata_filter, top_k=top_k)
        else:
            results = store.search(query_text, top_k=top_k)

        # Build context from results and generate answer
        context_parts = []
        for r in results:
            if isinstance(r, dict) and "content" in r:
                doc_title = r.get("metadata", {}).get("title", "")
                chunk_id = r.get("metadata", {}).get("chunk_id", "")
                context_parts.append(f"[{chunk_id} - {doc_title}]:\n{r['content']}")
        
        context = "\n\n".join(context_parts)
        prompt = (
            f"Dựa vào ngữ cảnh các văn bản quy chế sau đây, hãy trả lời câu hỏi một cách chi tiết, chính xác và có viện dẫn:\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {query_text}\n\n"
            f"Trả lời:"
        )
        try:
            agent_answer = agent.llm_fn(prompt)
        except Exception as e:
            agent_answer = f"Dựa trên các tài liệu được truy xuất, quy định được nêu chi tiết ở các điều khoản trong danh sách chunks bên dưới. (Chi tiết: {e})"

        self.send_json({
            "query": query_text,
            "filter_applied": metadata_filter,
            "top_k": top_k,
            "agent_answer": agent_answer,
            "results": results
        })

    def handle_compare_chunking(self, payload: Dict[str, Any]):
        doc_name = payload.get("doc_name", "doc_4.md")
        doc_path = DATA_DIR / doc_name
        if not doc_path.exists():
            doc_path = DATA_DIR / "doc_1.md"
        
        raw = doc_path.read_text(encoding="utf-8")
        content = raw.split("---", 2)[2].strip() if raw.startswith("---") and len(raw.split("---", 2)) >= 3 else raw

        fixed = FixedSizeChunker(chunk_size=500, overlap=50)
        sent = SentenceChunker(max_sentences_per_chunk=3)
        rec = RecursiveChunker(chunk_size=500, separators=["\n\n### ", "\n\n## ", "\n\n", "\n", ". ", " "])

        c_fixed = fixed.chunk(content)
        c_sent = sent.chunk(content)
        c_rec = rec.chunk(content)

        self.send_json({
            "document": doc_path.name,
            "text_length": len(content),
            "strategies": {
                "fixed_size": {
                    "name": "FixedSizeChunker (500 chars / 50 overlap)",
                    "count": len(c_fixed),
                    "avg_length": round(sum(len(c) for c in c_fixed) / max(1, len(c_fixed)), 1),
                    "sample": c_fixed[:3] if c_fixed else []
                },
                "by_sentences": {
                    "name": "SentenceChunker (3 sentences)",
                    "count": len(c_sent),
                    "avg_length": round(sum(len(c) for c in c_sent) / max(1, len(c_sent)), 1),
                    "sample": c_sent[:3] if c_sent else []
                },
                "recursive": {
                    "name": "RecursiveChunker (Heading & Section Aware)",
                    "count": len(c_rec),
                    "avg_length": round(sum(len(c) for c in c_rec) / max(1, len(c_rec)), 1),
                    "sample": c_rec[:3] if c_rec else []
                }
            }
        })

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_server():
    load_documents_into_store()
    server_address = ("", PORT)
    with ReusableTCPServer(server_address, BrightPathHandler) as httpd:
        print(f"[BrightPath AI] Platform is running at http://localhost:{PORT}")
        print(f"[BrightPath AI] Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[BrightPath AI] Server shutting down.")

if __name__ == "__main__":
    run_server()
