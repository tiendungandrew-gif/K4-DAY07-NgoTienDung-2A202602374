import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from src.models import Document
from src.store import EmbeddingStore
from src.chunking import HeadingSectionChunker
from src.embeddings import _mock_embed
from src.agent import KnowledgeBaseAgent

DATA_DIR = Path("data/university") if Path("data/university").exists() else Path("data")

QUERIES = [
    {
        "id": 1,
        "query": "Trường tổ chức cho sinh viên đăng ký học muộn nhất bao lâu trước khi bắt đầu học kỳ?",
        "filter": None,
        "gold": "Trường tổ chức cho sinh viên đăng ký học muộn nhất 3 tuần trước thời điểm bắt đầu học kỳ.",
        "markers": ["muộn nhất 3 tuần", "muon nhat 3 tuan"],
    },
    {
        "id": 2,
        "query": "Học cải thiện điểm được tối đa bao nhiêu tín chỉ trong học kỳ 1?",
        "filter": None,
        "gold": "Sinh viên chỉ được học cải thiện điểm không quá 8 tín chỉ đối với học kỳ 1 và học kỳ 3; không quá 5 tín chỉ đối với học kỳ 2.",
        "markers": ["không quá 8 tín chỉ", "khong qua 8 tin chi", "8 tín chỉ đối với học kỳ 1"],
    },
    {
        "id": 3,
        "query": "Khi không đồng ý với điểm thi thì làm gì?",
        "filter": {"audience": "student"},
        "gold": "Điểm thành phần: khiếu nại trực tiếp giảng viên. Điểm thi học phần: nộp đơn xin xem lại bài tại Phòng Thanh tra, ĐBCLGD & Khảo thí.",
        "markers": ["khiếu nại trực tiếp", "khieu nai truc tiep", "xem lại kết quả bài thi", "Phòng Thanh tra"],
    },
    {
        "id": 4,
        "query": "Sinh viên được tuyển chọn vào chương trình Chất lượng cao như thế nào?",
        "filter": None,
        "gold": "Xét tuyển thẳng nếu đáp ứng yêu cầu tiếng Anh: thành viên đội tuyển Olympic quốc tế; và các diện tuyển thẳng khác theo quy định CLC.",
        "markers": ["xét tuyển thẳng", "xet tuyen thang", "Olympic quốc tế", "chất lượng cao"],
    },
    {
        "id": 5,
        "query": "Điều kiện để được xét công nhận tốt nghiệp gồm những gì?",
        "filter": None,
        "gold": "Sinh viên được xét tốt nghiệp khi đủ điều kiện tại Điều 30: không bị kỷ luật đình chỉ, tích lũy đủ học phần, GPA từ 2,00, chứng chỉ GDQP-GDTC, hoàn thành nghĩa vụ học phí, v.v.",
        "markers": ["Điều 30", "công nhận tốt nghiệp", "cong nhan tot nghiep", "xét và công nhận tốt nghiệp", "tích lũy đủ"],
    },
]


def _fold(text: str) -> str:
    table = str.maketrans(
        "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
        "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ",
        "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd"
        "AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD",
    )
    return text.translate(table).lower().replace("ƣ", "u")


def parse_md_file(path: Path):
    text = path.read_text(encoding="utf-8")
    frontmatter = {}
    content = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()
            for key, raw in re.findall(r"^(\w+):\s*(.+)$", parts[1], re.M):
                frontmatter[key] = raw.strip().strip("\"'").rstrip("\r")
    return frontmatter, content


def lexical_overlap(query: str, text: str) -> float:
    q = set(re.findall(r"\w+", _fold(query)))
    t = set(re.findall(r"\w+", _fold(text)))
    if not q:
        return 0.0
    return len(q & t) / len(q)


def contains_marker(text: str, markers: list[str]) -> bool:
    folded = _fold(text)
    for m in markers:
        if _fold(m) in folded:
            return True
    return False


def hybrid_rank(records: list[dict], query: str, top_k: int) -> list[dict]:
    scored = []
    for r in records:
        lex = lexical_overlap(query, r["content"])
        vec = float(r.get("score", 0.0))
        hybrid = 0.75 * lex + 0.25 * ((vec + 1.0) / 2.0)
        item = dict(r)
        item["lexical"] = lex
        item["hybrid"] = hybrid
        scored.append(item)
    scored.sort(key=lambda x: x["hybrid"], reverse=True)
    return scored[:top_k]


def filter_records(store: EmbeddingStore, metadata_filter: dict | None) -> list[dict]:
    if not metadata_filter:
        return list(store._store)
    return [
        r
        for r in store._store
        if all(str(r["metadata"].get(k, "")).strip() == str(v) for k, v in metadata_filter.items())
    ]


def extractive_answer(question: str, results: list[dict], gold: str, markers: list[str]) -> str:
    joined = "\n".join(r["content"] for r in results)
    if contains_marker(joined, markers):
        for r in results:
            if contains_marker(r["content"], markers):
                snippet = re.sub(r"\s+", " ", r["content"]).strip()
                return snippet[:420]
    return (
        "Không tìm thấy đoạn văn bản chứa đáp án trong top-3. "
        f"Gold (để đối chiếu): {gold}"
    )


def run_benchmark():
    print(f"=== Running Benchmark on {DATA_DIR} ===")
    print("Strategy: HeadingSectionChunker + hybrid (lexical 0.75 + mock-vector 0.25)")
    print("Embedder: MockEmbedder (no semantics) — lexical rerank is required for a fair gold check.\n")

    chunker = HeadingSectionChunker(chunk_size=900)
    all_chunk_docs = []
    md_files = sorted(p for p in DATA_DIR.glob("*.md"))

    for path in md_files:
        fm, body = parse_md_file(path)
        chunks = chunker.chunk(body)
        for i, chunk_text in enumerate(chunks):
            all_chunk_docs.append(
                Document(
                    id=f"{path.stem}#{i}",
                    content=chunk_text,
                    metadata={
                        **fm,
                        "doc_id": fm.get("doc_id", path.stem),
                        "chunk_index": i,
                    },
                )
            )

    print(f"Loaded {len(md_files)} files -> Generated {len(all_chunk_docs)} chunk Documents.")

    store = EmbeddingStore(collection_name="benchmark_store", embedding_fn=_mock_embed)
    store.add_documents(all_chunk_docs)
    print(f"Stored {store.get_collection_size()} chunks in EmbeddingStore.\n")

    def llm_fn(prompt: str) -> str:
        return prompt[-200:]

    agent = KnowledgeBaseAgent(store=store, llm_fn=llm_fn)

    output_lines = [
        f"BENCHMARK RESULTS - {DATA_DIR}",
        "Strategy: HeadingSectionChunker + hybrid lexical/vector",
        f"Total documents: {len(md_files)}, Total chunks: {len(all_chunk_docs)}",
        "Embedder: MockEmbedder (hash) + lexical rerank because mock has no semantics",
        "",
    ]

    personal_rows = []
    scores = []

    for item in QUERIES:
        qid = item["id"]
        qtext = item["query"]
        qfilter = item["filter"]
        markers = item["markers"]
        gold = item["gold"]

        header = f"Query {qid}: {qtext}"
        if qfilter:
            header += f" [Filter: {qfilter}]"
        print(header)
        output_lines.append(header)
        output_lines.append(f"  Gold: {gold}")

        filtered = filter_records(store, qfilter)
        print(f"  Candidates after filter: {len(filtered)}")
        output_lines.append(f"  Candidates after filter: {len(filtered)}")

        vector_top = store.search_with_filter(qtext, top_k=3, metadata_filter=qfilter)
        hybrid_top = hybrid_rank(
            store.search_with_filter(qtext, top_k=max(1, len(filtered)), metadata_filter=qfilter)
            if filtered
            else [],
            qtext,
            3,
        )

        output_lines.append("  -- Vector-only (MockEmbedder) top-3 --")
        for rank, res in enumerate(vector_top, start=1):
            preview = res["content"][:100].replace("\n", " ")
            line = (
                f"    Rank {rank} | Score: {res['score']:.4f} | "
                f"{res['metadata'].get('doc_id')}#{res['metadata'].get('chunk_index')} | {preview}..."
            )
            output_lines.append(line)

        output_lines.append("  -- Hybrid (chấm điểm chốt) top-3 --")
        print("  Hybrid top-3:")
        hit_rank = None
        for rank, res in enumerate(hybrid_top, start=1):
            preview = res["content"][:120].replace("\n", " ")
            doc_id = res["metadata"].get("doc_id", "unknown")
            c_idx = res["metadata"].get("chunk_index", 0)
            relevant = contains_marker(res["content"], markers)
            if relevant and hit_rank is None:
                hit_rank = rank
            flag = "RELEVANT" if relevant else "not-relevant"
            line = (
                f"    Rank {rank} | hybrid={res['hybrid']:.4f} lex={res['lexical']:.3f} "
                f"vec={res['score']:.4f} | {doc_id}#{c_idx} | [{flag}] | {preview}..."
            )
            print("   ", line.strip())
            output_lines.append(line)

        answer = extractive_answer(qtext, hybrid_top, gold, markers)
        in_top3 = hit_rank is not None
        if hit_rank == 1 and in_top3:
            qscore = 2
        elif in_top3:
            qscore = 1
        else:
            qscore = 0
        scores.append(qscore)

        output_lines.append(f"  Gold in top-3: {'YES rank=' + str(hit_rank) if in_top3 else 'NO'}")
        output_lines.append(f"  Score (2/1/0): {qscore}")
        output_lines.append(f"  Agent (extractive from retrieved context): {answer[:300]}")
        output_lines.append("")
        print(f"  Gold in top-3: {in_top3} (rank={hit_rank}) -> {qscore}/2\n")

        top1 = hybrid_top[0] if hybrid_top else {}
        personal_rows.append(
            {
                "id": qid,
                "query": qtext,
                "top1": re.sub(r"\s+", " ", top1.get("content", ""))[:80] if top1 else "",
                "score": f"{top1.get('hybrid', 0):.3f}" if top1 else "n/a",
                "relevant": in_top3,
                "rank": hit_rank,
                "answer": answer[:180],
                "qscore": qscore,
            }
        )

        if qid == 3:
            no_filter = hybrid_rank(
                store.search_with_filter(qtext, top_k=store.get_collection_size(), metadata_filter=None),
                qtext,
                3,
            )
            output_lines.append("  A/B without metadata_filter:")
            for rank, res in enumerate(no_filter, start=1):
                aud = res["metadata"].get("audience")
                preview = res["content"][:90].replace("\n", " ")
                output_lines.append(
                    f"    Rank {rank} | audience={aud} | {res['metadata'].get('doc_id')} | {preview}..."
                )
            with_ids = [r["metadata"].get("doc_id") for r in hybrid_top]
            without_ids = [r["metadata"].get("doc_id") for r in no_filter]
            same = with_ids == without_ids
            output_lines.append(
                f"  A/B identical top-3? {'YES (câu hỏi chưa thật sự cần filter)' if same else 'NO — filter đổi kết quả'}"
            )
            output_lines.append("")

    total = sum(scores)
    output_lines.append(f"RETRIEVAL QUALITY: {total} / 10")
    output_lines.append("Rubric: 2 if gold in top-1 + answerable context; 1 if gold in top-2/3; 0 if missing.")
    print(f"RETRIEVAL QUALITY: {total} / 10")

    Path("ket_qua_benchmark.txt").write_text("\n".join(output_lines), encoding="utf-8")
    print("Saved benchmark results to ket_qua_benchmark.txt")
    return personal_rows, total


if __name__ == "__main__":
    run_benchmark()
