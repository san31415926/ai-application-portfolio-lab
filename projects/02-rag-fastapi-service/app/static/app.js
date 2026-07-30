let activeNoteId = null;
let answerSources = [];
let answerText = "";
let thinkingText = "";
let autoSaveTimer = null;
let autoSaveVersion = 0;

const elements = {
  state: document.querySelector("#service-state"),
  chatModel: document.querySelector("#chat-model"),
  assistModel: document.querySelector("#assist-model"),
  metricDocuments: document.querySelector("#metric-documents"),
  metricChunks: document.querySelector("#metric-chunks"),
  metricNotes: document.querySelector("#metric-notes"),
  metricReviews: document.querySelector("#metric-reviews"),
  documentCount: document.querySelector("#document-count"),
  sourceCount: document.querySelector("#source-count"),
  noteCount: document.querySelector("#note-count"),
  reviewCount: document.querySelector("#review-count"),
  activeNoteLabel: document.querySelector("#active-note-label"),
  documentList: document.querySelector("#document-list"),
  sourceList: document.querySelector("#source-list"),
  noteList: document.querySelector("#note-list"),
  reviewList: document.querySelector("#review-list"),
  chunksPanel: document.querySelector("#chunks-panel"),
  chunksTitle: document.querySelector("#chunks-title"),
  chunksList: document.querySelector("#chunks-list"),
  answerStatus: document.querySelector("#answer-status"),
  answerOutput: document.querySelector("#answer-output"),
  thinkingShell: document.querySelector("#thinking-shell"),
  thinkingOutput: document.querySelector("#thinking-output"),
  showThinking: document.querySelector("#show-thinking"),
  assistStatus: document.querySelector("#assist-status"),
  assistOutput: document.querySelector("#assist-output"),
  queryInput: document.querySelector("#query-input"),
  topK: document.querySelector("#top-k"),
  minScore: document.querySelector("#min-score"),
  noteTitle: document.querySelector("#note-title"),
  noteCategory: document.querySelector("#note-category"),
  noteTags: document.querySelector("#note-tags"),
  noteContent: document.querySelector("#note-content"),
  assistMode: document.querySelector("#assist-mode"),
  assistButton: document.querySelector("#assist-button"),
  queryButton: document.querySelector("#query-form button[type='submit']"),
  toast: document.querySelector("#toast"),
};

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => elements.toast.classList.remove("show"), 2200);
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const detail = typeof payload === "object" ? payload.detail || payload.message : payload;
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return payload;
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("zh-CN");
}

function setState(status, label) {
  elements.state.className = `service-state ${status}`;
  elements.state.textContent = label;
}

function emptyNode(label) {
  const node = window.document.createElement("div");
  node.className = "empty-state";
  node.textContent = label;
  return node;
}

function parseTags(value) {
  return value
    .split(/[,，、\s]+/)
    .map((tag) => tag.trim().replace(/^#/, ""))
    .filter(Boolean);
}

function currentNotePayload() {
  return {
    title: elements.noteTitle.value.trim(),
    content: elements.noteContent.value.trim(),
    category: elements.noteCategory.value.trim() || "未分类",
    tags: parseTags(elements.noteTags.value),
  };
}

function cancelAutoSave() {
  autoSaveVersion += 1;
  window.clearTimeout(autoSaveTimer);
  autoSaveTimer = null;
}

function scheduleAutoSave() {
  if (!activeNoteId) return;
  window.clearTimeout(autoSaveTimer);
  const version = ++autoSaveVersion;
  elements.activeNoteLabel.textContent = "等待同步到后台...";
  autoSaveTimer = window.setTimeout(() => autoSaveNote(version), 900);
}

async function autoSaveNote(version) {
  if (version !== autoSaveVersion || !activeNoteId) return;
  const noteId = activeNoteId;
  const payload = currentNotePayload();
  if (!payload.title || !payload.content) {
    elements.activeNoteLabel.textContent = "填写标题和内容后自动同步";
    return;
  }
  elements.activeNoteLabel.textContent = "正在同步到后台...";
  try {
    const response = await api(`/api/v1/notes/${noteId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify(payload),
    });
    if (version !== autoSaveVersion || activeNoteId !== noteId) return;
    elements.activeNoteLabel.textContent = `已同步到后台：${response.data.title}`;
    await refreshNotes();
  } catch (error) {
    if (version === autoSaveVersion && activeNoteId === noteId) {
      elements.activeNoteLabel.textContent = "同步失败，请点击保存重试";
      showToast(`自动保存失败：${error.message}`);
    }
  }
}

async function refreshStats() {
  const [knowledgePayload, notePayload] = await Promise.all([
    api("/api/v1/knowledge/stats"),
    api("/api/v1/notes/stats"),
  ]);
  const knowledge = knowledgePayload.data || {};
  const notes = notePayload.data || {};
  elements.metricDocuments.textContent = formatNumber(knowledge.document_count);
  elements.metricChunks.textContent = formatNumber(knowledge.chunk_count);
  elements.metricNotes.textContent = formatNumber(notes.note_count);
  elements.metricReviews.textContent = formatNumber(notes.review_due_count);
}

async function refreshModels() {
  try {
    const payload = await api("/api/v1/models");
    const modelData = payload.data || {};
    const models = modelData.models || [];
    const modelSelects = [elements.chatModel, elements.assistModel].filter(Boolean);
    if (!models.length) {
      modelSelects.forEach((select) => {
        select.replaceChildren(new Option("暂无本地模型", ""));
        select.disabled = true;
      });
      return;
    }
    const defaultModel = modelData.default_model;
    modelSelects.forEach((select) => {
      select.replaceChildren();
      models.forEach((model) => {
        const label = model.parameter_size ? `${model.name} · ${model.parameter_size}` : model.name;
        select.append(new Option(label, model.name));
      });
      select.value = models.some((model) => model.name === defaultModel)
        ? defaultModel
        : models[0].name;
      select.disabled = false;
    });
  } catch (error) {
    [elements.chatModel, elements.assistModel].filter(Boolean).forEach((select) => {
      select.replaceChildren(new Option("模型服务不可用", ""));
      select.disabled = true;
    });
  }
}

function renderDocuments(documents) {
  elements.documentList.replaceChildren();
  elements.documentCount.textContent = `${documents.length} 份文档`;

  if (!documents.length) {
    elements.documentList.append(emptyNode("暂无文档"));
    return;
  }

  documents.forEach((doc) => {
    const card = window.document.createElement("article");
    card.className = "document-card";

    const body = window.document.createElement("div");
    const title = window.document.createElement("p");
    title.className = "card-title";
    title.textContent = doc.filename;
    const meta = window.document.createElement("p");
    meta.className = "card-meta";
    meta.textContent = `${doc.chunk_count} 个切片 · ${formatNumber(doc.character_count)} 字符 · ${doc.content_type}`;
    body.append(title, meta);

    const actions = window.document.createElement("div");
    actions.className = "card-actions";
    const chunksButton = window.document.createElement("button");
    chunksButton.className = "ghost-button compact";
    chunksButton.textContent = "切片";
    chunksButton.addEventListener("click", () => showChunks(doc));
    const deleteButton = window.document.createElement("button");
    deleteButton.className = "ghost-button compact";
    deleteButton.textContent = "删除";
    deleteButton.addEventListener("click", () => deleteDocument(doc.document_id));
    actions.append(chunksButton, deleteButton);

    card.append(body, actions);
    elements.documentList.append(card);
  });
}

async function refreshDocuments() {
  const payload = await api("/api/v1/knowledge/documents");
  renderDocuments(payload.data || []);
}

function renderSources(sources) {
  elements.sourceList.replaceChildren();
  elements.sourceCount.textContent = `${sources.length} 条来源`;

  if (!sources.length) {
    elements.sourceList.append(emptyNode("暂无来源"));
    return;
  }

  sources.forEach((source, index) => {
    const card = window.document.createElement("article");
    card.className = "source-card";

    const header = window.document.createElement("header");
    const title = window.document.createElement("button");
    title.className = "source-link card-title";
    title.textContent = `[来源${index + 1}] ${source.filename} · 第 ${source.chunk_index} 段`;
    title.type = "button";
    title.title = "打开原文切片";
    title.setAttribute("aria-label", `打开 ${source.filename} 第 ${source.chunk_index} 段原文`);
    title.addEventListener("click", () => showSourceChunk(source));
    const score = window.document.createElement("span");
    score.className = "score";
    score.textContent = source.score.toFixed(4);
    header.append(title, score);

    const content = window.document.createElement("pre");
    content.className = "source-content";
    content.textContent = source.content;
    card.append(header, content);
    elements.sourceList.append(card);
  });
}

function renderAnswerText(text) {
  elements.answerOutput.replaceChildren();
  const citationPattern = /\[?\s*来源\s*(\d+)\s*\]?/g;
  let cursor = 0;
  let match;
  while ((match = citationPattern.exec(text)) !== null) {
    if (match.index > cursor) {
      elements.answerOutput.append(window.document.createTextNode(text.slice(cursor, match.index)));
    }
    const source = answerSources[Number(match[1]) - 1];
    if (!source) {
      elements.answerOutput.append(window.document.createTextNode(match[0]));
    } else {
      const button = window.document.createElement("button");
      button.type = "button";
      button.className = "answer-source-link";
      button.textContent = `[来源${match[1]}]`;
      button.title = `打开${source.filename}第${source.chunk_index}段原文`;
      button.setAttribute("aria-label", `打开${source.filename}第${source.chunk_index}段原文`);
      button.addEventListener("click", () => {
        showSourceChunk(source).catch((error) => showToast(error.message));
      });
      elements.answerOutput.append(button);
    }
    cursor = citationPattern.lastIndex;
  }
  if (cursor < text.length) {
    elements.answerOutput.append(window.document.createTextNode(text.slice(cursor)));
  }
}

function appendAnswerText(text) {
  answerText += text;
  renderAnswerText(answerText);
}

function renderNotes(notes) {
  elements.noteList.replaceChildren();
  elements.noteCount.textContent = `${notes.length} 条`;

  if (!notes.length) {
    elements.noteList.append(emptyNode("暂无笔记"));
    return;
  }

  notes.forEach((note) => {
    const card = window.document.createElement("article");
    card.className = note.note_id === activeNoteId ? "note-card selected" : "note-card";

    const title = window.document.createElement("p");
    title.className = "card-title";
    title.textContent = note.title;
    const meta = window.document.createElement("p");
    meta.className = "card-meta";
    meta.textContent = `${note.category} · ${note.tags.join(" / ") || "无标签"}`;
    const preview = window.document.createElement("p");
    preview.className = "note-preview";
    preview.textContent = note.content.slice(0, 96);

    const actions = window.document.createElement("div");
    actions.className = "card-actions";
    const editButton = window.document.createElement("button");
    editButton.className = "ghost-button compact";
    editButton.textContent = "编辑";
    editButton.addEventListener("click", () => selectNote(note));
    const deleteButton = window.document.createElement("button");
    deleteButton.className = "ghost-button compact";
    deleteButton.textContent = "删除";
    deleteButton.addEventListener("click", () => deleteNote(note.note_id));
    actions.append(editButton, deleteButton);

    card.append(title, meta, preview, actions);
    elements.noteList.append(card);
  });
}

function renderReviews(notes) {
  elements.reviewList.replaceChildren();
  elements.reviewCount.textContent = `${notes.length} 条`;

  if (!notes.length) {
    elements.reviewList.append(emptyNode("暂无待回顾"));
    return;
  }

  notes.forEach((note) => {
    const card = window.document.createElement("article");
    card.className = "note-card";
    const title = window.document.createElement("p");
    title.className = "card-title";
    title.textContent = note.title;
    const meta = window.document.createElement("p");
    meta.className = "card-meta";
    meta.textContent = `已回顾 ${note.review_count} 次 · ${note.category}`;
    const button = window.document.createElement("button");
    button.className = "ghost-button compact";
    button.textContent = "完成回顾";
    button.addEventListener("click", () => completeReview(note.note_id));
    card.append(title, meta, button);
    elements.reviewList.append(card);
  });
}

async function refreshNotes() {
  const payload = await api("/api/v1/notes");
  renderNotes(payload.data || []);
}

async function refreshReviews() {
  const payload = await api("/api/v1/reviews/due");
  renderReviews(payload.data || []);
}

async function refreshAll() {
  await Promise.all([refreshStats(), refreshDocuments(), refreshNotes(), refreshReviews()]);
}

async function loadSamples() {
  const payload = await api("/api/v1/knowledge/documents/samples", { method: "POST" });
  await refreshAll();
  const count = (payload.data || []).length;
  showToast(count ? `已导入 ${count} 份教程` : "教程库已就绪");
}

async function loadNoteSamples() {
  const payload = await api("/api/v1/notes/samples", { method: "POST" });
  await refreshAll();
  const notes = payload.data || [];
  if (notes.length) {
    selectNote(notes[0]);
  }
  showToast(notes.length ? `已导入 ${notes.length} 条笔记` : "笔记已就绪");
}

async function clearKnowledge() {
  await api("/api/v1/knowledge/documents", { method: "DELETE" });
  await refreshAll();
  renderSources([]);
  answerSources = [];
  elements.answerStatus.textContent = "待查询";
  elements.answerStatus.className = "answer-status";
  answerText = "未查询";
  renderAnswerText(answerText);
  thinkingText = "";
  elements.thinkingOutput.textContent = "";
  elements.thinkingShell.hidden = true;
  elements.chunksPanel.hidden = true;
  showToast("知识库已清空");
}

async function uploadDocument(event) {
  event.preventDefault();
  const input = document.querySelector("#document-file");
  const file = input.files[0];
  if (!file) {
    showToast("请选择文件");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  await api("/api/v1/knowledge/documents/upload", {
    method: "POST",
    body: formData,
  });
  input.value = "";
  await refreshAll();
  showToast("文档已索引");
}

async function queryKnowledge(event) {
  event.preventDefault();
  const query = elements.queryInput.value.trim();
  if (!query) {
    showToast("请输入问题");
    return;
  }

  elements.queryButton.disabled = true;
  elements.queryButton.textContent = "生成中...";
  elements.answerStatus.textContent = "检索中";
  elements.answerStatus.className = "answer-status";
  answerText = "";
  renderAnswerText(answerText);
  thinkingText = "";
  elements.thinkingOutput.textContent = "";
  elements.thinkingShell.hidden = !elements.showThinking.checked;

  try {
    const response = await fetch("/api/v1/chat/query/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({
        query,
        top_k: Number(elements.topK.value),
        min_score: Number(elements.minScore.value),
        show_thinking: elements.showThinking.checked,
        chat_model: elements.chatModel.value || null,
      }),
    });
    if (!response.ok || !response.body) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    const handleEvent = (block) => {
      const line = block.split("\n").find((item) => item.startsWith("data: "));
      if (!line) return;
      const payload = JSON.parse(line.slice(6));
      if (payload.type === "meta") {
        answerSources = payload.sources || [];
        renderSources(answerSources);
        elements.thinkingShell.hidden = !elements.showThinking.checked;
        elements.answerStatus.textContent = payload.refused
          ? "已拒答"
          : payload.answer_model
            ? `模型生成中 · ${payload.answer_model}`
            : "正在整理答案";
        elements.answerStatus.className = payload.refused ? "answer-status refused" : "answer-status";
      } else if (payload.type === "delta") {
        appendAnswerText(payload.text);
        elements.answerStatus.textContent = "正在生成...";
      } else if (payload.type === "thinking") {
        thinkingText += payload.text;
        elements.thinkingOutput.textContent = thinkingText;
        elements.thinkingShell.hidden = false;
        elements.answerStatus.textContent = "正在思考...";
      } else if (payload.type === "replace") {
        answerText = payload.text;
        renderAnswerText(answerText);
      } else if (payload.type === "done") {
        const modelLabel = payload.answer_model ? ` · ${payload.answer_model}` : "";
        elements.answerStatus.textContent = payload.refused
          ? "已拒答"
          : payload.answer_backend === "ollama"
            ? `回答完成${modelLabel}`
            : "回答完成（提取式）";
        elements.answerStatus.className = payload.refused ? "answer-status refused" : "answer-status";
      }
    };

    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const blocks = buffer.split("\n\n");
      buffer = blocks.pop() || "";
      blocks.forEach(handleEvent);
      if (done) break;
    }
    if (buffer.trim()) handleEvent(buffer);
  } catch (error) {
    elements.answerStatus.textContent = "生成失败，请重试";
    elements.answerStatus.className = "answer-status refused";
    throw error;
  } finally {
    elements.queryButton.disabled = false;
    elements.queryButton.textContent = "查询";
  }
}

function selectNote(note) {
  cancelAutoSave();
  activeNoteId = note.note_id;
  elements.activeNoteLabel.textContent = `正在编辑：${note.title}`;
  elements.noteTitle.value = note.title;
  elements.noteCategory.value = note.category;
  elements.noteTags.value = note.tags.join(", ");
  elements.noteContent.value = note.content;
  refreshNotes().catch((error) => showToast(error.message));
}

function newNote() {
  cancelAutoSave();
  activeNoteId = null;
  elements.activeNoteLabel.textContent = "新建笔记";
  elements.noteTitle.value = "";
  elements.noteCategory.value = "";
  elements.noteTags.value = "";
  elements.noteContent.value = "";
  elements.assistOutput.textContent = "暂无内容";
}

async function saveNote(event) {
  event.preventDefault();
  cancelAutoSave();
  const payload = currentNotePayload();
  if (!payload.title || !payload.content) {
    showToast("标题和内容不能为空");
    return;
  }

  const response = activeNoteId
    ? await api(`/api/v1/notes/${activeNoteId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify(payload),
      })
    : await api("/api/v1/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify(payload),
      });

  selectNote(response.data);
  await refreshAll();
  showToast("笔记已保存到后台");
}

async function deleteNote(noteId) {
  await api(`/api/v1/notes/${noteId}`, { method: "DELETE" });
  if (activeNoteId === noteId) {
    newNote();
  }
  await refreshAll();
  showToast("笔记已删除");
}

async function showRelatedSources() {
  if (!activeNoteId) {
    showToast("未选择笔记");
    return;
  }
  const payload = await api(`/api/v1/notes/${activeNoteId}/related?top_k=${Number(elements.topK.value)}`);
  renderSources(payload.data || []);
  showToast("已根据当前笔记检索相关来源");
}

async function assistWriting() {
  if (!activeNoteId) {
    showToast("未选择笔记");
    return;
  }
  elements.assistButton.disabled = true;
  elements.assistButton.textContent = "模型生成中...";
  elements.assistStatus.textContent = `正在调用 ${elements.assistModel.value || "本地模型"}`;
  try {
    const payload = await api(`/api/v1/notes/${activeNoteId}/assist`, {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({
        mode: elements.assistMode.value,
        chat_model: elements.assistModel.value || null,
      }),
    });
    elements.assistOutput.textContent = payload.data.result;
    elements.assistStatus.textContent = payload.data.answer_model
      ? `本地模型：${payload.data.answer_model}`
      : "规则降级结果";
    renderSources(payload.data.related_sources || []);
  } finally {
    elements.assistButton.disabled = false;
    elements.assistButton.textContent = "写作辅助";
  }
}

async function completeReview(noteId) {
  await api(`/api/v1/reviews/${noteId}/complete`, { method: "POST" });
  await refreshAll();
  showToast("已记录回顾");
}

async function showSourceChunk(source) {
  await showChunks(source, source.chunk_index);
  showToast(`已打开 ${source.filename} 第 ${source.chunk_index} 段原文`);
}

async function showChunks(doc, selectedChunkIndex = null) {
  const payload = await api(`/api/v1/knowledge/documents/${doc.document_id}/chunks`);
  elements.chunksTitle.textContent = `${doc.filename} · 文档切片`;
  elements.chunksList.replaceChildren();
  let selectedCard = null;
  (payload.data || []).forEach((chunk) => {
    const card = window.document.createElement("article");
    card.className = selectedChunkIndex === chunk.chunk_index ? "chunk-card selected" : "chunk-card";
    if (selectedChunkIndex === chunk.chunk_index) {
      selectedCard = card;
    }
    const title = window.document.createElement("p");
    title.className = "card-title";
    title.textContent = `第 ${chunk.chunk_index} 段`;
    const content = window.document.createElement("pre");
    content.className = "chunk-content";
    content.textContent = chunk.content;
    card.append(title, content);
    elements.chunksList.append(card);
  });
  elements.chunksPanel.hidden = false;
  elements.chunksPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  if (selectedCard) {
    selectedCard.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

async function deleteDocument(documentId) {
  await api(`/api/v1/knowledge/documents/${documentId}`, { method: "DELETE" });
  await refreshAll();
  showToast("文档已删除");
}

async function boot() {
  try {
    await api("/health");
    setState("ok", "服务正常");
    renderSources([]);
    await refreshModels();
    await refreshAll();
  } catch (error) {
    setState("error", "连接失败");
    showToast(error.message);
  }
}

document.querySelector("#load-samples-button").addEventListener("click", () => {
  loadSamples().catch((error) => showToast(error.message));
});
document.querySelector("#load-note-samples-button").addEventListener("click", () => {
  loadNoteSamples().catch((error) => showToast(error.message));
});
document.querySelector("#clear-button").addEventListener("click", () => {
  clearKnowledge().catch((error) => showToast(error.message));
});
document.querySelector("#upload-form").addEventListener("submit", (event) => {
  uploadDocument(event).catch((error) => showToast(error.message));
});
document.querySelector("#query-form").addEventListener("submit", (event) => {
  queryKnowledge(event).catch((error) => showToast(error.message));
});
document.querySelector("#note-form").addEventListener("submit", (event) => {
  saveNote(event).catch((error) => showToast(error.message));
});
[elements.noteTitle, elements.noteCategory, elements.noteTags, elements.noteContent].forEach((field) => {
  field.addEventListener("input", scheduleAutoSave);
});
document.querySelector("#new-note-button").addEventListener("click", newNote);
document.querySelector("#related-button").addEventListener("click", () => {
  showRelatedSources().catch((error) => showToast(error.message));
});
document.querySelector("#assist-button").addEventListener("click", () => {
  assistWriting().catch((error) => showToast(error.message));
});
document.querySelector("#close-chunks-button").addEventListener("click", () => {
  elements.chunksPanel.hidden = true;
});

boot();
