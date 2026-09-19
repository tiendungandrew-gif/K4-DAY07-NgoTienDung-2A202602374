import os
import sys
import re
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from src.models import Document
from src.store import EmbeddingStore
from src.chunking import RecursiveChunker, SentenceChunker, FixedSizeChunker
from src.embeddings import _mock_embed

DATA_DIR = Path("data/university") if Path("data/university").exists() else Path("data")

QUERIES = [
    {
        "id": 1,
        "query": "Chương trình Tiên tiến tại ĐH Kinh tế Quốc dân đào tạo những chuyên ngành nào?",
        "filter": None
    },
    {
        "id": 2,
        "query": "Một tín chỉ tại Trường Đại học Kinh tế Quốc dân được quy định bằng bao nhiêu tiết học lý thuyết và bao nhiêu giờ tự học?",
        "filter": None
    },
    {
        "id": 3,
        "query": "Học phần tương đương được quy định phải có nội dung giống tối thiểu bao nhiêu phần trăm so với học phần xem xét?",
        "filter": None
    },
    {
        "id": 4,
        "query": "Sinh viên chương trình Tiên tiến có điểm thang 10 dưới 4,5 thì xếp điểm chữ gì và quy đổi sang thang điểm 4 là bao nhiêu?",
        "filter": None
    },
    {
        "id": 5,
        "query": "Những trường hợp nào sinh viên không được tiếp tục theo học Chương trình Tiên tiến và phải trở lại ngành cũ?",
        "filter": {"audience": "student"}
    }
]

def parse_md_file(path: Path):
    text = path.read_text(encoding="utf-8")
    frontmatter = {}
    content = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_raw = parts[1]
            content = parts[2].strip()
            frontmatter = dict(re.findall(r'^(\w+):\s*(.+)$', fm_raw, re.M))
    return frontmatter, content

def run_benchmark():
    print(f"=== Running Benchmark on {DATA_DIR} ===")
    
    # 1. Choose Chunker strategy (RecursiveChunker by default for L3A)
    chunker = RecursiveChunker(chunk_size=500)
    
    # 2. Load and Chunk files
    all_chunk_docs = []
    md_files = sorted([p for p in DATA_DIR.glob("*.md") if p.name.startswith("doc_")])
    
    for path in md_files:
        fm, body = parse_md_file(path)
        chunks = chunker.chunk(body)
        for i, chunk_text in enumerate(chunks):
            doc = Document(
                id=f"{path.stem}#{i}",
                content=chunk_text,
                metadata={
                    **fm,
                    "doc_id": fm.get("doc_id", path.stem),
                    "chunk_index": i
                }
            )
            all_chunk_docs.append(doc)
            
    print(f"Loaded {len(md_files)} files -> Generated {len(all_chunk_docs)} chunk Documents.")
    
    # 3. Store into EmbeddingStore
    store = EmbeddingStore(collection_name="benchmark_store", embedding_fn=_mock_embed)
    store.add_documents(all_chunk_docs)
    print(f"Stored {store.get_collection_size()} chunks in EmbeddingStore.\n")
    
    # 4. Run Queries and collect output
    output_lines = []
    output_lines.append(f"BENCHMARK RESULTS - {DATA_DIR}")
    output_lines.append(f"Total documents: {len(md_files)}, Total chunks: {len(all_chunk_docs)}\n")
    
    for item in QUERIES:
        qid = item["id"]
        qtext = item["query"]
        qfilter = item["filter"]
        
        header = f"Query {qid}: {qtext}"
        if qfilter:
            header += f" [Filter: {qfilter}]"
        print(header)
        output_lines.append(header)
        
        results = store.search_with_filter(qtext, top_k=3, metadata_filter=qfilter)
        for rank, res in enumerate(results, start=1):
            doc_id = res['metadata'].get('doc_id', 'unknown')
            c_idx = res['metadata'].get('chunk_index', 0)
            score = res['score']
            preview = res['content'][:120].replace('\n', ' ')
            
            line = f"  Rank {rank} | Score: {score:.4f} | {doc_id}#{c_idx} | {preview}..."
            print(line)
            output_lines.append(line)
            
        print()
        output_lines.append("")
        
    with open("ket_qua_benchmark.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Saved benchmark results to ket_qua_benchmark.txt")

if __name__ == "__main__":
    run_benchmark()
