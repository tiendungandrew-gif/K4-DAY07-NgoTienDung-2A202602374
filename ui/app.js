/**
 * BrightPath AI — Interactive Frontend Logic
 * Phenomenon Studio Design System
 */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSearch();
  initPresets();
  loadDocuments();
  initChunkingLab();
  loadBenchmarkData();
});

// Tab Switching
function initTabs() {
  const navItems = document.querySelectorAll(".nav-item");
  const tabPanels = document.querySelectorAll(".tab-panel");

  navItems.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabId = btn.getAttribute("data-tab");
      navItems.forEach((b) => b.classList.remove("active"));
      tabPanels.forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPanel = document.getElementById(`tab-${tabId}`);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }
    });
  });
}

// Search and RAG Agent interaction
function initSearch() {
  const btnSearch = document.getElementById("btn-search");
  const queryInput = document.getElementById("query-input");
  const audienceFilter = document.getElementById("filter-audience");
  const topKSelect = document.getElementById("filter-topk");

  btnSearch.addEventListener("click", () => {
    const query = queryInput.value.trim();
    if (!query) return;

    let filter = null;
    if (audienceFilter.value) {
      filter = { audience: audienceFilter.value };
    }
    const topK = parseInt(topKSelect.value, 10) || 3;
    executeQuery(query, filter, topK);
  });

  queryInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      btnSearch.click();
    }
  });
}

// Preset pills
function initPresets() {
  const presetPills = document.querySelectorAll(".preset-pill");
  const queryInput = document.getElementById("query-input");
  const audienceFilter = document.getElementById("filter-audience");
  const btnSearch = document.getElementById("btn-search");

  presetPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      const q = pill.getAttribute("data-query");
      const f = pill.getAttribute("data-filter");

      queryInput.value = q;
      if (f) {
        try {
          const parsed = JSON.parse(f);
          if (parsed.audience) {
            audienceFilter.value = parsed.audience;
          }
        } catch (e) {
          audienceFilter.value = "";
        }
      } else {
        audienceFilter.value = "";
      }

      btnSearch.click();
    });
  });
}

// Execute query through backend
async function executeQuery(query, filter, topK) {
  const resultsArea = document.getElementById("results-area");
  const agentAnswerText = document.getElementById("agent-answer-text");
  const chunksContainer = document.getElementById("chunks-container");

  resultsArea.style.display = "flex";
  agentAnswerText.textContent = "Đang tìm kiếm trong 1.605 chunks và sinh câu trả lời RAG...";
  chunksContainer.innerHTML = "<div style='color: #94A3B8; font-size: 13px;'>Đang tải chunks...</div>";

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        metadata_filter: filter,
        top_k: topK
      })
    });

    const data = await res.json();
    if (data.error) {
      agentAnswerText.textContent = `Lỗi: ${data.error}`;
      chunksContainer.innerHTML = "";
      return;
    }

    // Render Agent response
    agentAnswerText.textContent = data.agent_answer || "Không tìm thấy nội dung phù hợp trong kho tài liệu.";

    // Render Chunks
    chunksContainer.innerHTML = "";
    if (!data.results || data.results.length === 0) {
      chunksContainer.innerHTML = "<div style='color: #94A3B8; font-size: 13px;'>Không có chunk nào khớp với bộ lọc.</div>";
      return;
    }

    data.results.forEach((item, index) => {
      const score = item.score !== undefined ? Number(item.score).toFixed(4) : "0.0000";
      const scorePercent = Math.min(100, Math.max(0, Number(score) * 100));
      const docId = (item.metadata && item.metadata.doc_id) || "N/A";
      const chunkId = (item.metadata && item.metadata.chunk_id) || `chunk_${index}`;
      const audience = (item.metadata && item.metadata.audience) || "all";
      const dept = (item.metadata && item.metadata.department) || "general";
      const version = (item.metadata && item.metadata.document_version) || "2024";

      const card = document.createElement("div");
      card.className = "chunk-item-card";
      card.innerHTML = `
        <div class="chunk-item-header">
          <div class="chunk-rank-badge">
            <span class="rank-tag">TOP ${index + 1}</span>
            <span class="chunk-id-tag">${chunkId} (${docId})</span>
          </div>
          <div class="chunk-score-meter">
            <span class="score-text">Score: ${score}</span>
            <div class="score-bar-bg">
              <div class="score-bar-fill" style="width: ${scorePercent}%"></div>
            </div>
          </div>
        </div>
        <div class="chunk-content-text">${escapeHtml(item.content)}</div>
        <div class="chunk-meta-badges">
          <span class="meta-pill">audience: ${audience}</span>
          <span class="meta-pill">department: ${dept}</span>
          <span class="meta-pill">version: ${version}</span>
        </div>
      `;
      chunksContainer.appendChild(card);
    });

  } catch (err) {
    agentAnswerText.textContent = `Lỗi kết nối máy chủ RAG: ${err.message}`;
    chunksContainer.innerHTML = "";
  }
}

// Load Documents
async function loadDocuments() {
  const container = document.getElementById("docs-grid-container");
  const docCountNav = document.getElementById("nav-doc-count");
  const refreshBtn = document.getElementById("btn-refresh-docs");

  if (refreshBtn) {
    refreshBtn.addEventListener("click", loadDocuments);
  }

  try {
    const res = await fetch("/api/documents");
    const docs = await res.json();
    if (docCountNav) docCountNav.textContent = docs.length;

    container.innerHTML = "";
    docs.forEach((doc) => {
      const card = document.createElement("div");
      card.className = "doc-card";
      card.innerHTML = `
        <div class="doc-card-top">
          <span class="doc-id-pill">${doc.doc_id}</span>
          <span class="doc-audience-pill ${doc.audience === 'student' ? 'student' : 'all'}">${doc.audience}</span>
        </div>
        <div class="doc-card-title">${escapeHtml(doc.title)}</div>
        <div class="doc-card-preview">${escapeHtml(doc.preview)}</div>
        <div class="doc-card-footer">
          <span>${doc.char_count.toLocaleString()} ký tự</span>
          <span>Dept: ${doc.department}</span>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (e) {
    container.innerHTML = `<div style='color: #F87171'>Không thể tải danh sách tài liệu: ${e.message}</div>`;
  }
}

// Chunking lab
function initChunkingLab() {
  const btnRun = document.getElementById("btn-run-compare");
  const docSelect = document.getElementById("compare-doc-select");
  const container = document.getElementById("compare-results-container");

  if (!btnRun) return;

  btnRun.addEventListener("click", async () => {
    container.innerHTML = "<div style='color: #94A3B8'>Đang phân tích các chiến lược chunking...</div>";
    try {
      const res = await fetch("/api/compare_chunking", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doc_name: docSelect.value })
      });
      const data = await res.json();
      container.innerHTML = "";

      const strats = data.strategies;
      for (const key in strats) {
        const item = strats[key];
        const isBest = key === "recursive";
        const card = document.createElement("div");
        card.className = `compare-strategy-card ${isBest ? "best" : ""}`;
        card.innerHTML = `
          <div class="compare-title">${item.name} ${isBest ? "⭐ (Khuyên dùng)" : ""}</div>
          <div class="compare-metrics-grid">
            <div class="metric-box">
              <div class="metric-box-num">${item.count}</div>
              <div class="metric-box-lbl">Số lượng Chunks</div>
            </div>
            <div class="metric-box">
              <div class="metric-box-num">${item.avg_length}</div>
              <div class="metric-box-lbl">Độ dài TB (chars)</div>
            </div>
          </div>
          <div class="sample-chunks-box">
            <strong>Mẫu Chunk 1:</strong><br>
            ${escapeHtml(item.sample[0] || "Trống")}
          </div>
        `;
        container.appendChild(card);
      }
    } catch (e) {
      container.innerHTML = `<div style='color: #F87171'>Lỗi phân tích: ${e.message}</div>`;
    }
  });

  // Run automatically on first load
  btnRun.click();
}

// Load Benchmark Data
async function loadBenchmarkData() {
  const benchPre = document.getElementById("raw-benchmark-content");
  if (!benchPre) return;
  try {
    const res = await fetch("/api/benchmark");
    const data = await res.json();
    benchPre.textContent = data.raw;
  } catch (e) {
    benchPre.textContent = "Không thể tải ket_qua_benchmark.txt";
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
