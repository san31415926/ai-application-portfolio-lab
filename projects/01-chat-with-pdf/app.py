from __future__ import annotations

import html
import re
from pathlib import Path

import streamlit as st

from career_database import (
    DEFAULT_DB_PATH,
    ensure_database,
    interview_pack,
    learning_plan,
    project_recommendations,
    role_skill_matrix,
    safe_select,
    search_jobs,
)
from jd_knowledge_base import (
    DEFAULT_SOURCE_PATHS,
    KnowledgeBase,
    RetrievalResult,
    answer_question,
    detect_skills,
    format_snippet,
    load_documents,
    relative_source,
)


DEFAULT_QUESTIONS = [
    "这个岗位要求哪些技能？",
    "我应该先学什么？",
    "这个项目怎么写进简历？",
    "面试官可能追问什么？",
]

RESUME_BULLETS = [
    "基于 Python 实现 AI 岗位 JD 知识库 MVP，支持读取 Markdown/PDF、文本切分、轻量检索和来源片段展示。",
    "设计低置信度拒答机制，当检索证据不足时拒绝编造答案，并用单元测试覆盖关键路径。",
    "将 Chat with PDF 学习项目改造成求职资料问答助手，用于分析岗位技能、学习路径、简历亮点和面试追问。",
]

SOURCE_TITLES = {
    "ai_application_engineer_jd.md": "AI 应用工程师岗位 JD",
    "rag_learning_notes.md": "RAG 学习笔记",
    "README.md": "项目 README",
    "notes.md": "实现记录",
}


@st.cache_data(show_spinner=False)
def build_knowledge_base(source_values: tuple[str, ...]) -> KnowledgeBase:
    paths = [Path(value) for value in source_values]
    documents = load_documents(paths)
    return KnowledgeBase.from_documents(documents)


def render_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #f5f7fb;
            --panel: #ffffff;
            --panel-soft: #f8fafc;
            --text: #17202a;
            --muted: #667085;
            --line: #d9e2ec;
            --teal: #0f766e;
            --blue: #2563eb;
            --amber: #b7791f;
            --green-soft: #e8f6f3;
            --blue-soft: #edf4ff;
            --amber-soft: #fff7e6;
        }
        .stApp {
            background: var(--bg);
            color: var(--text);
        }
        .block-container {
            max-width: 1260px;
            padding-top: 1.1rem;
            padding-bottom: 2.2rem;
        }
        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--line);
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.25rem;
        }
        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--text);
        }
        .top-panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-top: 4px solid var(--teal);
            border-radius: 8px;
            padding: 20px 22px;
            margin-bottom: 16px;
        }
        .eyebrow {
            color: var(--teal);
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .title {
            font-size: 32px;
            font-weight: 760;
            margin: 0 0 8px 0;
        }
        .subtitle {
            color: var(--muted);
            font-size: 15px;
            line-height: 1.65;
            max-width: 920px;
        }
        .status-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
        }
        .badge {
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 13px;
            font-weight: 650;
            border: 1px solid var(--line);
            background: var(--panel-soft);
            color: #344054;
        }
        .badge-green {
            background: var(--green-soft);
            border-color: #b6e0d8;
            color: var(--teal);
        }
        .badge-blue {
            background: var(--blue-soft);
            border-color: #c9ddff;
            color: var(--blue);
        }
        .badge-amber {
            background: var(--amber-soft);
            border-color: #f3d08b;
            color: var(--amber);
        }
        .metric-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 14px 16px;
            min-height: 92px;
        }
        .metric-label {
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 8px;
        }
        .metric-value {
            color: var(--text);
            font-size: 25px;
            font-weight: 760;
        }
        .metric-note {
            color: var(--muted);
            font-size: 12px;
            margin-top: 4px;
        }
        .section-panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 16px;
        }
        .section-title {
            font-size: 18px;
            font-weight: 750;
            margin-bottom: 6px;
        }
        .section-help {
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 14px;
        }
        .source-card {
            background: var(--panel-soft);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 10px;
        }
        .source-title {
            font-size: 14px;
            font-weight: 720;
            color: var(--text);
            margin-bottom: 6px;
        }
        .source-meta {
            color: var(--muted);
            font-size: 12px;
        }
        .answer-box {
            background: #fbfdff;
            border: 1px solid var(--line);
            border-left: 4px solid var(--blue);
            border-radius: 8px;
            padding: 16px 18px;
            white-space: pre-wrap;
            line-height: 1.65;
            font-size: 14px;
        }
        .resume-line {
            background: var(--panel-soft);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 10px;
            line-height: 1.6;
        }
        div[data-testid="stButton"] > button {
            border-radius: 8px;
            border: 1px solid #cfd8e3;
            background: #ffffff;
            color: #17202a;
            min-height: 42px;
            white-space: normal;
        }
        div[data-testid="stButton"] > button:hover {
            border-color: var(--teal);
            color: var(--teal);
        }
        div[data-testid="stButton"] > button[kind="primary"] {
            background: var(--teal);
            border-color: var(--teal);
            color: #ffffff;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            background: #ffffff;
            border: 1px solid var(--line);
            padding: 10px 16px;
        }
        .stTabs [aria-selected="true"] {
            border-color: var(--teal);
            color: var(--teal);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_source_card(path: Path, chunk_count: int) -> None:
    title = html.escape(SOURCE_TITLES.get(path.name, path.stem))
    source_path = html.escape(relative_source(path))
    st.markdown(
        f"""
        <div class="source-card">
            <div class="source-title">{title}</div>
            <div class="source-meta">{source_path}</div>
            <div class="source-meta" style="margin-top:6px;">已索引片段：{chunk_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chunk_count_by_source(knowledge_base: KnowledgeBase) -> dict[Path, int]:
    counts: dict[Path, int] = {}
    for chunk in knowledge_base.chunks:
        counts[chunk.source] = counts.get(chunk.source, 0) + 1
    return counts


def clean_answer_text(answer: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", answer.strip())


def render_result_card(result: RetrievalResult, index: int) -> None:
    source_title = html.escape(SOURCE_TITLES.get(result.chunk.source.name, result.chunk.source.stem))
    source = html.escape(relative_source(result.chunk.source))
    matched = html.escape("、".join(result.matched_terms[:8]) if result.matched_terms else "无")
    snippet = html.escape(format_snippet(result.chunk.text, width=360))
    st.markdown(
        f"""
        <div class="source-card">
            <div class="source-title">[{index}] {source_title} - 第 {result.chunk.index} 段</div>
            <div class="source-meta">{source}</div>
            <div class="source-meta" style="margin-top:6px;">相关度：{result.score:.3f}　命中词：{matched}</div>
            <div style="margin-top:8px; color:#344054; line-height:1.6;">{snippet}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def set_question(question: str) -> None:
    st.session_state["active_question"] = question


st.set_page_config(page_title="AI 岗位 JD 知识库", layout="wide")
render_css()

ensure_database(DEFAULT_DB_PATH)
source_values = tuple(str(path) for path in DEFAULT_SOURCE_PATHS)
knowledge_base = build_knowledge_base(source_values)
source_counts = chunk_count_by_source(knowledge_base)

if "active_question" not in st.session_state:
    st.session_state["active_question"] = DEFAULT_QUESTIONS[0]

with st.sidebar:
    st.markdown("### 数据源")
    for path in DEFAULT_SOURCE_PATHS:
        render_source_card(path, source_counts.get(path, 0))

    st.divider()
    st.markdown("### 检索设置")
    top_k = st.slider("返回来源数量", min_value=2, max_value=6, value=4)

    st.divider()
    st.markdown("### 项目状态")
    st.write("MVP 可运行")
    st.write("本地检索")
    st.write("SQLite 模拟数据库")
    st.write("中文界面")
    st.write("来源引用")

st.markdown(
    """
    <div class="top-panel">
        <div class="eyebrow">AI 应用工程作品集项目</div>
        <div class="title">AI 岗位 JD 知识库</div>
        <div class="subtitle">
            面向 AI 应用工程师求职场景，把岗位 JD、RAG 学习笔记和项目文档变成可检索知识库。
            页面聚焦三件事：回答岗位问题、展示来源证据、沉淀可以写进简历的项目材料。
        </div>
        <div class="status-row">
            <span class="badge badge-green">MVP 可运行</span>
            <span class="badge badge-blue">本地 RAG 风格检索</span>
            <span class="badge badge-amber">证据不足自动拒答</span>
            <span class="badge">中文求职场景</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
with metric_cols[0]:
    metric_card("数据源", str(len(DEFAULT_SOURCE_PATHS)), "JD、学习笔记、README、项目记录")
with metric_cols[1]:
    metric_card("索引片段", str(len(knowledge_base.chunks)), "文本切片 + 重叠窗口")
with metric_cols[2]:
    metric_card("默认问题", str(len(DEFAULT_QUESTIONS)), "技能、学习、简历、面试")
with metric_cols[3]:
    metric_card("测试状态", "8/8", "检索、拒答、数据库查询")

tab_workbench, tab_database, tab_sources, tab_resume = st.tabs(["问答工作台", "模拟数据库", "来源证据", "简历素材"])

with tab_workbench:
    left, right = st.columns([1.55, 1])

    with left:
        st.markdown(
            """
            <div class="section-panel">
                <div class="section-title">选择一个求职问题</div>
                <div class="section-help">先用固定问题演示，再输入自己的岗位或项目问题。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        quick_cols = st.columns(2)
        for index, question in enumerate(DEFAULT_QUESTIONS):
            with quick_cols[index % 2]:
                if st.button(question, key=f"quick-{index}", use_container_width=True):
                    set_question(question)

        user_question = st.text_area(
            "当前问题",
            value=st.session_state["active_question"],
            height=94,
            label_visibility="collapsed",
        )
        ask_clicked = st.button("检索并生成回答", type="primary", use_container_width=True)

        if ask_clicked:
            st.session_state["active_question"] = user_question.strip() or DEFAULT_QUESTIONS[0]

        active_question = st.session_state["active_question"]
        results = knowledge_base.retrieve(active_question, top_k=top_k)
        answer = clean_answer_text(answer_question(active_question, results))

        with st.chat_message("user"):
            st.write(active_question)
        with st.chat_message("assistant"):
            st.markdown(f'<div class="answer-box">{html.escape(answer)}</div>', unsafe_allow_html=True)

    with right:
        st.markdown(
            """
            <div class="section-panel">
                <div class="section-title">命中能力</div>
                <div class="section-help">根据当前检索片段自动识别，可用于简历技能区。</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        skills = detect_skills(results)
        if skills:
            st.markdown(
                '<div class="status-row">'
                + "".join(f'<span class="badge badge-blue">{skill}</span>' for skill in skills[:10])
                + "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("当前问题没有命中明确技能标签。")

        st.markdown("#### 最高相关来源")
        if results:
            for index, result in enumerate(results[:3], start=1):
                render_result_card(result, index)
        else:
            st.warning("没有检索到可用来源。")

with tab_database:
    st.markdown(
        """
        <div class="section-panel">
            <div class="section-title">AI 求职模拟数据库</div>
            <div class="section-help">这是一套本地 SQLite 业务库，用来查询岗位、技能、项目、学习任务和面试题之间的关系。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    jobs = search_jobs()
    role_options = {f"{row['id']} - {row['title']}｜{row['company_type']}": row["id"] for row in jobs}
    selected_role_label = st.selectbox("选择目标岗位", list(role_options.keys()))
    selected_role_id = role_options[selected_role_label]

    db_cols = st.columns([1, 1])
    with db_cols[0]:
        keyword = st.text_input("岗位关键词搜索", value="", placeholder="例如：RAG、Agent、数据分析")
        st.dataframe(search_jobs(keyword), use_container_width=True, hide_index=True)

    with db_cols[1]:
        st.markdown("#### 数据库结构")
        st.markdown(
            """
            - `roles`: 模拟岗位
            - `skills`: 技能库
            - `role_skills`: 岗位与技能要求
            - `projects`: 作品集项目
            - `project_skills`: 项目覆盖技能
            - `interview_questions`: 面试题
            - `learning_tasks`: 学习任务
            """
        )

    matrix_tab, project_tab, interview_tab, plan_tab, sql_tab = st.tabs(
        ["技能矩阵", "项目推荐", "面试题包", "学习任务", "只读 SQL"]
    )

    with matrix_tab:
        st.dataframe(role_skill_matrix(selected_role_id), use_container_width=True, hide_index=True)

    with project_tab:
        st.dataframe(project_recommendations(selected_role_id), use_container_width=True, hide_index=True)

    with interview_tab:
        st.dataframe(interview_pack(selected_role_id), use_container_width=True, hide_index=True)

    with plan_tab:
        status_filter = st.selectbox("任务状态", ["", "待开始", "已完成", "进行中"], format_func=lambda value: value or "全部")
        st.dataframe(learning_plan(status_filter), use_container_width=True, hide_index=True)

    with sql_tab:
        sql = st.text_area(
            "输入 SELECT 查询",
            value=(
                "SELECT r.title AS 岗位, s.name AS 技能, rs.importance AS 重要性, rs.evidence_required AS 需要证据\n"
                "FROM role_skills rs\n"
                "JOIN roles r ON r.id = rs.role_id\n"
                "JOIN skills s ON s.id = rs.skill_id\n"
                "WHERE r.id = 1\n"
                "ORDER BY rs.importance DESC;"
            ),
            height=190,
        )
        if st.button("运行只读查询", use_container_width=True):
            try:
                st.dataframe(safe_select(sql), use_container_width=True, hide_index=True)
            except ValueError as exc:
                st.error(str(exc))

with tab_sources:
    st.markdown(
        """
        <div class="section-panel">
            <div class="section-title">来源证据面板</div>
            <div class="section-help">展示当前知识库如何把文件拆成可检索片段。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for path in DEFAULT_SOURCE_PATHS:
        render_source_card(path, source_counts.get(path, 0))

    st.markdown("#### 当前问题的检索片段")
    for index, result in enumerate(knowledge_base.retrieve(st.session_state["active_question"], top_k=top_k), start=1):
        render_result_card(result, index)

with tab_resume:
    st.markdown(
        """
        <div class="section-panel">
            <div class="section-title">可写进简历的项目材料</div>
            <div class="section-help">保持真实口径：当前是 MVP，不写生产级、不写真实用户量。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for bullet in RESUME_BULLETS:
        st.markdown(f'<div class="resume-line">{bullet}</div>', unsafe_allow_html=True)

    st.markdown("#### 面试讲法")
    st.markdown(
        """
        - 输入：岗位 JD、RAG 学习笔记、项目 README 和实现记录。
        - 处理：读取文本、切分 chunk、构建轻量检索索引、按问题返回相关片段。
        - 输出：中文回答、来源片段、相关度、命中词和拒答提示。
        - 下一步：接入 embeddings、Chroma/FAISS、文件上传和更完整的评估集。
        """
    )
