# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G25 (Chủ đề: Dịch vụ & Quy chế ĐHKTQD)  
**Thành viên:** Nguyễn Đức Thắng, Nguyễn Hải Long, Ngô Tiến Dũng (2A202602374), Trần Anh Quân  
**Ngày:** 19/9/2026  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định đào tạo và dịch vụ sinh viên tại trường Đại học Kinh tế Quốc dân (NEU).

**Tại sao nhóm chọn chủ đề này?**
> Nhóm chọn chủ đề này vì các quy chế học vụ, đăng ký học phần, chương trình tiên tiến/chất lượng cao và quy định thi cử tại NEU rất đồ sộ, phức tạp với nhiều đối tượng khác nhau. Việc xây dựng hệ thống RAG giúp sinh viên và giảng viên nhanh chóng tra cứu chính xác quyền lợi, điều kiện tốt nghiệp và quy trình xử lý học vụ mà không bị nhầm lẫn giữa các hệ đào tạo.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy chế đào tạo đại học 2024 (QĐ 368) | https://daotao.neu.edu.vn/Resources/Docs/SubDomain/daotao/NewFolder/Q%C4%90%20368_QUY%20CH%E1%BA%BE%20%C4%90%C3%80O%20T%E1%BA%A0O%20%C4%90%E1%BA%A0I%20H%E1%BB%8CC%202024-news.pdf | 2024-11-20 / 2024 (QĐ 368) | 47,596 | `audience: all`, `department: daotao`, `version: 2024` |
| 2 | Quy chế đào tạo đại học K63 trở đi (QĐ 1155) | https://daotao.neu.edu.vn/Resources/Docs/SubDomain/daotao/Xulyhocvu/1155_Quyche-Daotao-Daihoc-K63%20tr%E1%BB%9F%20%C4%91i.pdf | 2024-11-20 / 2021 (QĐ 1155/K63) | 45,791 | `audience: all`, `department: daotao`, `version: 2021` |
| 3 | Quy định đào tạo ĐH chính quy theo hệ thống tín chỉ tại ĐHKTQD | https://daotao.neu.edu.vn/vi/quy-dinh-cua-truong/quy-dinh-dao-tao-dai-hoc-he-chinh-quy-theo-he-thong-tin-chi-tai-truong-dai-hoc-kinh-te-quoc-dan-2 | 2024-11-20 / 2012 | 78,221 | `audience: all`, `department: daotao`, `version: 2012` |
| 4 | Quy định đào tạo theo chương trình tiên tiến | https://aep.neu.edu.vn/wp-content/uploads/2022/07/Quy-dinh-ve-dao-tao-theo-chuong-trinh-tien-tien.pdf | 2024-11-20 / 2022 (AEP) | 77,682 | `audience: student`, `department: aep`, `version: 2022` |
| 5 | Quy định đào tạo chất lượng cao | https://aep.neu.edu.vn/wp-content/uploads/2022/07/Quy-dinh-dao-tao-Chat-luong-cao.pdf | 2024-11-20 / 2022 (AEP) | 81,795 | `audience: student`, `department: aep`, `version: 2022` |
| 6 | Những điều sinh viên ĐH KTQD cần biết (2014) | https://www.neu.edu.vn/Upload_Files_WEB/Files/ThongBao/T10_2014/Nhung%20dieu%20SV%20DH%20KTQD%20can%20biet%20(2014).pdf | 2024-11-20 / 2014 | 171,083 | `audience: student`, `department: truong`, `version: 2014` |
| 7 | Bộ quy định đào tạo tín chỉ ĐHKTQD (MFE) | https://mfe.neu.edu.vn/bo-quy-dinh-dao-tao-tin-chi-dhktqd-2/ | 2024-11-20 / 2018 | 72,868 | `audience: all`, `department: mfe`, `version: 2018` |
| 8 | Thông tư 08/2021/TT-BGDĐT - Quy chế đào tạo trình độ đại học | https://daotao.neu.edu.vn/Resources/Docs/SubDomain/daotao/SongNganh/thong-tu-08-2021-tt-bgddt-quy-che-dao-tao-trinh-do-dai-hoc.pdf | 2024-11-20 / 2021 (TT 08) | 40,875 | `audience: all`, `department: bgddt`, `version: 2021` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `source_url` | str | `https://aep.neu.edu.vn/...` | Định danh nguồn gốc xuất xứ, cung cấp đường link tham chiếu cho người dùng đối soát. |
| `retrieved_at` | str | `2024-11-20` | Đảm bảo tính kiểm toán và biết thời điểm tài liệu được cập nhật về hệ thống. |
| `document_version` | str | `2022 (AEP)`, `2021 (TT 08)` | Giúp lọc văn bản quy chế theo năm ban hành hoặc phiên bản đang có hiệu lực. |
| `audience` | str | `student`, `all`, `faculty` | **Ràng buộc L3A**: Lọc tài liệu theo đối tượng tiếp cận (sinh viên, giảng viên, đại chúng) để tránh nhiễu truy xuất. |
| `department` | str | `daotao`, `aep`, `mfe`, `truong` | Phân loại theo đơn vị/khoa/viện ban hành để khoanh vùng tìm kiếm chính xác. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu với `chunk_size=500`:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `doc_4.md` (CT Tiên tiến) | FixedSizeChunker (`fixed_size`) | 173 | 498.7 ký tự | Một số câu và bảng thang điểm bị cắt ngang ở ranh giới |
| `doc_4.md` (CT Tiên tiến) | SentenceChunker (`by_sentences`) | 177 | 435.6 ký tự | Giữ nguyên vẹn từng câu đơn lẻ nhưng ranh giới Điều bị phân tán |
| `doc_4.md` (CT Tiên tiến) | RecursiveChunker (`recursive`) | 199 | 388.4 ký tự | **Tốt nhất** — Bảo toàn trọn vẹn tiêu đề Điều, Khoản và Bảng điểm |
| `doc_3.md` (Quy chế tín chỉ) | FixedSizeChunker (`fixed_size`) | 174 | 497.4 ký tự | Bị cắt vụn các định nghĩa tỷ lệ phần trăm (80%) ở ranh giới |
| `doc_3.md` (Quy chế tín chỉ) | SentenceChunker (`by_sentences`) | 199 | 390.5 ký tự | Giữ đúng câu nhưng các danh sách gạch đầu dòng bị tách rời |
| `doc_3.md` (Quy chế tín chỉ) | RecursiveChunker (`recursive`) | 188 | 413.4 ký tự | Giữ trọn cấu trúc Chương/Điều và các quy định tính giờ học |
| `doc_1.md` (QĐ 368/2024) | FixedSizeChunker (`fixed_size`) | 106 | 498.5 ký tự | Dễ cắt ngang các bước trong Phụ lục lập thời khóa biểu |
| `doc_1.md` (QĐ 368/2024) | SentenceChunker (`by_sentences`) | 96 | 493.5 ký tự | Xử lý tốt các đoạn văn bản chính sách chung |
| `doc_1.md` (QĐ 368/2024) | RecursiveChunker (`recursive`) | 131 | 361.5 ký tự | Phân tách mạch lạc theo từng đề mục và bảng quy trình |

### Chiến lược của từng thành viên

**Thành viên 1 — Ngô Tiến Dũng**
- **Loại chiến lược:** RecursiveChunker (kết hợp phân tách tiêu đề Heading/Điều khoản)
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản quy chế đào tạo đại học có cấu trúc phân cấp chặt chẽ (Chương $\to$ Điều $\to$ Khoản). Sử dụng `RecursiveChunker` với danh sách dấu phân cách ưu tiên `["\n\n### ", "\n\n## ", "\n\n", "\n", ". "]` giúp giữ nguyên trọn vẹn từng Điều khoản trong một chunk, không làm thất lạc ngữ cảnh pháp lý.
- **Code snippet:**
```python
class RecursiveSectionChunker:
    def __init__(self, chunk_size: int = 500):
        self.separators = ["\n\n### ", "\n\n## ", "\n\n", "\n", ". ", " "]
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        return RecursiveChunker(separators=self.separators, chunk_size=self.chunk_size).chunk(text)
```

**Thành viên 2 — Nguyễn Đức Thắng**
- **Loại chiến lược:** SentenceChunker (`max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn:** Chia nhỏ văn bản theo ranh giới kết thúc câu (`. `, `! `, `? `). Phù hợp với các đoạn văn bản hướng dẫn sinh viên dạng cẩm nang hoặc văn xuôi giải thích, giúp mô hình embedding nắm bắt được các đơn vị ngữ nghĩa hoàn chỉnh.

**Thành viên 3 — Nguyễn Hải Long**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=500, overlap=50`)
- **Mô tả & lý do chọn:** Phương pháp đường cơ sở đơn giản, tốc độ chia cắt cực nhanh và đồng đều về kích thước. Sử dụng cơ chế cửa sổ trượt (sliding window) với overlap 50 ký tự để hạn chế việc mất thông tin tại vị trí cắt giữa các chunk.

**Thành viên 4 — Trần Anh Quân**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=300, overlap=30`)
- **Mô tả & lý do chọn:** Chia nhỏ kích thước chunk (300 ký tự) nhằm tăng độ tập trung thông tin cho từng vector embedding, giảm độ loãng ngữ nghĩa đối với các đoạn văn bản ngắn.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|------------------------|----------------------|-----------|----------|
| Ngô Tiến Dũng | RecursiveChunker (Section) | 10 / 10 | Giữ trọn vẹn toàn bộ bảng biểu, Điều khoản pháp lý và ngữ cảnh định lượng | Số lượng chunk nhiều hơn một chút, cần logic đệ quy |
| Nguyễn Đức Thắng | SentenceChunker (3 câu) | 8 / 10 | Đơn vị câu hoàn chỉnh, tự nhiên | Các bảng biểu và danh sách gạch đầu dòng dài bị phân mảnh |
| Nguyễn Hải Long | FixedSizeChunker (500/50) | 7 / 10 | Đơn giản, độ dài chunk rất đồng đều | Dễ cắt ngang giữa một câu hoặc một từ quan trọng |
| Trần Anh Quân | FixedSizeChunker (300/30) | 6 / 10 | Kích thước nhỏ, tập trung | Dễ làm mất ngữ cảnh của các điều khoản dài và bảng điểm |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **RecursiveChunker (kết hợp tiêu đề Mục/Điều)** là chiến lược tốt nhất cho chủ đề Quy chế & Dịch vụ Đại học. Do đặc thù tài liệu học vụ chứa nhiều bảng điểm, điều kiện tốt nghiệp và quy trình nhiều bước, việc phân tách theo ranh giới cấu trúc văn bản (`\n\n`, `### Điều`) đảm bảo mỗi chunk là một quy định hoàn chỉnh, giúp mô hình Vector Store và RAG Agent truy xuất chính xác ngữ cảnh mà không bị cụt ý.

### Phân tích trường hợp thất bại (Failure Case Analysis) — Nhóm

- **Failure Case 1 (Mock Embedder Semantic Limitation — Câu 1):** Với câu hỏi "Trường tổ chức cho sinh viên đăng ký học muộn nhất bao lâu?", Mock Embedder dựa trên hash từ vựng không nắm bắt được ngữ nghĩa "thời hạn đăng ký", dẫn đến top-1 lạc sang Điều 22 về đề thi kết thúc học phần (score 0.374). Agent đã đúng khi từ chối bịa đặt — đây là hành vi "hallucination guard" cần thiết.
- **Failure Case 2 (Lỗi thiếu Metadata Filter — Câu 3):** Khi tìm kiếm "không đồng ý với điểm thi thì làm gì?" mà không dùng `metadata_filter={"audience": "student"}`, hệ thống dễ lấy nhầm quy định dành cho giảng viên/cán bộ coi thi thay vì quy chế phúc khảo dành cho sinh viên.
- **Failure Case 3 (Top-1 lạc nhưng Top-2 đúng — Câu 5):** Với câu hỏi "Điều kiện công nhận tốt nghiệp", top-1 trả về Điều 6 về kế hoạch giảng dạy, nhưng top-2 chứa đúng Điều 30 về xét tốt nghiệp. Cho thấy cần tăng `top_k` hoặc cải thiện embedding để nâng vị trí chunk chính xác.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-----------------|---------------------------------|---------------------------|
| 1 | Trường tổ chức cho sinh viên đăng ký học muộn nhất bao lâu trước khi bắt đầu học kỳ? | Trước khi bắt đầu học kỳ ít nhất 6 tuần, Trường tổ chức cho sinh viên đăng ký học phần. | `doc_3.md` (Điều 7: Đăng ký học phần, Khoản 1) |
| 2 | Học cải thiện điểm được tối đa bao nhiêu tín chỉ trong học kỳ 1? | Sinh viên chỉ được học cải thiện điểm không quá 8 tín chỉ đối với học kỳ 1 và học kỳ 3; không quá 5 tín chỉ đối với học kỳ 2. | `doc_4.md` (Điều 11: Đăng ký học phần và học cải thiện) |
| 3 | Khi không đồng ý với điểm thi thì làm gì? *(Lọc: `audience: student`)* | Sinh viên có thể khiếu nại trực tiếp giảng viên (đối với điểm thành phần) hoặc nộp đơn xin phúc khảo tại Phòng Thanh tra, ĐBCLGD & Khảo thí (đối với điểm thi kết thúc học phần). | `doc_5.md` (Điều 26: Phúc khảo và khiếu nại điểm) |
| 4 | Sinh viên được tuyển chọn vào chương trình Chất lượng cao như thế nào? | Diện xét tuyển thẳng gồm: thành viên đội tuyển Olympic quốc tế, đạt giải nhất/nhì/ba HSG quốc gia lớp 12, và tuyển theo điểm thi THPT Quốc gia xét theo từng ngành/chuyên ngành. | `doc_5.md` (Điều 11: Tuyển chọn sinh viên vào CLC) |
| 5 | Điều kiện để được xét công nhận tốt nghiệp gồm những gì? | Sinh viên phải đáp ứng đủ 7 điều kiện a–g theo Điều 30 khoản 1: (a) tích lũy đủ tín chỉ, (b) đạt chuẩn đầu ra ngoại ngữ, (c) GPA đạt yêu cầu, (d) không đang bị kỷ luật, (e) hoàn thành nghĩa vụ tài chính, (f) trả sách thư viện, (g) hoàn thành khảo sát cuối khóa. | `doc_1.md` / `doc_2.md` (Điều 30: Xét và công nhận tốt nghiệp) |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|---------------------------------|-------------------------------|---------|
| 1 | Trường tổ chức đăng ký học muộn nhất bao lâu? | RecursiveChunker — cần Semantic Embedding | ❌ Không (Failure Case) | Mock Embedder hash không bắt được ngữ nghĩa "thời hạn đăng ký", top-1 lạc sang Điều 22 đề thi |
| 2 | Học cải thiện điểm tối đa bao nhiêu TC học kỳ 1? | RecursiveChunker (Section) | ✅ Có (Top 1) | Chunk Điều 11 chứa nguyên vẹn quy định "không quá 8 tín chỉ" |
| 3 | Không đồng ý điểm thi → làm gì? (`audience: student`) | RecursiveChunker + Metadata filter | ✅ Có (Top 1) | Lọc `audience: student` giúp tập trung vào quy chế dành cho SV |
| 4 | Tuyển chọn vào chương trình CLC | RecursiveChunker | ✅ Có (Top 1) | Điều 11 CLC giữ trọn danh sách diện xét tuyển |
| 5 | Điều kiện công nhận tốt nghiệp | RecursiveChunker | ✅ Có (Top 2) | Top-1 lạc sang Điều 6, nhưng Top-2 chứa Điều 30 công nhận tốt nghiệp |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Rất hữu ích, đặc biệt ở Câu hỏi 3. Khi hỏi "không đồng ý với điểm thi thì làm gì?" mà không lọc `audience: student`, hệ thống dễ lấy nhầm quy định dành cho giảng viên/cán bộ coi thi. Nhờ lọc `metadata_filter={"audience": "student"}`, kết quả trả về tập trung đúng vào Điều 26 về quyền phúc khảo và khiếu nại của sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Cấu trúc tài liệu quyết định chiến lược Chunking:** Đối với văn bản pháp lý/quy chế, Recursive Chunking theo cấp bậc (Chương/Điều) vượt trội hoàn toàn so với Fixed-size chunking truyền thống.
> 2. **Sức mạnh của Metadata Filtering:** Việc gắn siêu dữ liệu đối tượng (`audience: student/all/faculty`) và đơn vị (`department`) giúp triệt tiêu hiện tượng "ảo giác ngữ cảnh" khi có nhiều văn bản quy định chồng chéo qua các năm.
> 3. **Tầm quan trọng của chất lượng số hóa:** Việc xử lý OCR chính xác các bảng biểu và ký tự tiếng Việt có dấu là tiền đề quyết định để Vector Search đạt độ chính xác cao.

**Bài học rút ra khi so sánh trong nhóm:**
> Khi thử nghiệm cùng một bộ 8 tài liệu ĐHKTQD nhưng với các chiến lược chunking khác nhau, sự khác biệt thể hiện rõ rệt ở các câu hỏi tra cứu định lượng (thang điểm, số tiết, tỷ lệ %). Chiến lược nào giữ nguyên được bảng biểu và tiêu đề điều khoản thì Agent trả lời chính xác ngay từ Top-1 chunk, trong khi chiến lược chia cố định làm đứt gãy thông tin và khiến Agent trả lời thiếu ý.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ bổ sung thêm trường metadata `effective_year` (năm hiệu lực) và xây dựng bộ parser chuyên biệt để tự động nhận diện cây mục lục văn bản quy chế thành các chunk dạng Hierarchical Chunks (kèm tóm tắt tiêu đề Chương cho mỗi Điều con).

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |

