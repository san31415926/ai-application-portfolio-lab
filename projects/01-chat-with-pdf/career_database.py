from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "processed" / "ai_career_demo.sqlite"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS role_skills;
DROP TABLE IF EXISTS project_skills;
DROP TABLE IF EXISTS interview_questions;
DROP TABLE IF EXISTS learning_tasks;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    level TEXT NOT NULL,
    company_type TEXT NOT NULL,
    business_scenario TEXT NOT NULL,
    location TEXT NOT NULL,
    salary_range TEXT NOT NULL,
    priority INTEGER NOT NULL
);

CREATE TABLE skills (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    target_level TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE role_skills (
    role_id INTEGER NOT NULL REFERENCES roles(id),
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    importance INTEGER NOT NULL,
    evidence_required TEXT NOT NULL,
    PRIMARY KEY (role_id, skill_id)
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    stage TEXT NOT NULL,
    stack TEXT NOT NULL,
    resume_value TEXT NOT NULL,
    next_step TEXT NOT NULL
);

CREATE TABLE project_skills (
    project_id INTEGER NOT NULL REFERENCES projects(id),
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    evidence_status TEXT NOT NULL,
    PRIMARY KEY (project_id, skill_id)
);

CREATE TABLE interview_questions (
    id INTEGER PRIMARY KEY,
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    difficulty TEXT NOT NULL,
    question TEXT NOT NULL,
    strong_answer_hint TEXT NOT NULL
);

CREATE TABLE learning_tasks (
    id INTEGER PRIMARY KEY,
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    task_name TEXT NOT NULL,
    output_artifact TEXT NOT NULL,
    estimated_hours INTEGER NOT NULL,
    status TEXT NOT NULL
);
"""

ROLES = [
    (1, "初级 AI 应用工程师", "Junior", "内部 AI 工具团队", "销售、运营、客服知识库和自动化助手", "远程/一线城市", "12k-20k", 95),
    (2, "RAG 应用开发实习生", "Intern", "AI 初创公司", "企业文档问答、知识库检索、来源引用", "远程/上海", "6k-10k", 88),
    (3, "LLM 产品原型工程师", "Junior", "SaaS 公司", "把业务需求快速做成可演示 AI 原型", "北京/深圳", "14k-22k", 84),
    (4, "数据分析 AI 助手开发者", "Junior", "数据服务团队", "CSV/Excel 上传、自然语言分析和图表生成", "杭州/远程", "12k-18k", 76),
    (5, "Web Research Agent 开发者", "Junior", "咨询/投研工具团队", "网页搜索、资料抽取、结构化研究报告", "远程", "13k-21k", 72),
]

SKILLS = [
    (1, "Python", "编程基础", "能独立写脚本", "文件读取、数据处理、命令行参数、基础测试。"),
    (2, "PDF/Markdown 解析", "数据接入", "能处理常见文档", "从 PDF、Markdown、README 中提取干净文本。"),
    (3, "文本切分", "RAG", "理解 chunk_size 和 overlap", "把长文档切成适合检索的小片段。"),
    (4, "Embeddings", "RAG", "会调用模型生成向量", "把文本转成语义向量，用于相似度搜索。"),
    (5, "向量数据库", "RAG", "会用 Chroma 或 FAISS", "保存向量并按问题检索相关上下文。"),
    (6, "Prompt 设计", "LLM 应用", "能约束回答边界", "让模型基于来源回答，证据不足时拒答。"),
    (7, "来源引用", "可信回答", "能展示证据", "回答中展示片段来源、相关度和命中词。"),
    (8, "低置信度拒答", "可信回答", "能控制幻觉风险", "当检索分数低或证据不足时拒绝编造。"),
    (9, "Streamlit", "前端演示", "能做可用 demo", "为非技术用户提供上传、提问、查看来源的界面。"),
    (10, "SQLite", "数据工程", "能设计轻量业务库", "用关系表表达岗位、技能、项目和面试题。"),
    (11, "单元测试", "工程化", "能覆盖关键路径", "测试加载、检索、拒答和数据库查询。"),
    (12, "Git/GitHub", "工程化", "能维护作品集", "用 README、截图、提交记录展示项目演进。"),
    (13, "Agent 工具调用", "Agent", "理解工具选择", "根据问题调用搜索、文件读取或数据分析工具。"),
    (14, "数据分析", "业务分析", "会处理 CSV/Excel", "计算指标、发现异常、生成图表和摘要。"),
    (15, "网页信息抽取", "Research Agent", "会抽取网页内容", "从网页获取信息并整理成结构化报告。"),
    (16, "部署与配置", "工程化", "理解环境变量", "使用 .env.example、依赖文件和运行文档。"),
]

ROLE_SKILLS = [
    (1, 1, 5, "能展示 Python CLI 或 Streamlit 原型代码"),
    (1, 2, 5, "能读取岗位 JD、PDF 或 Markdown"),
    (1, 3, 5, "能解释为什么要切分文本"),
    (1, 4, 4, "能接入 embedding 模型或说明升级路径"),
    (1, 5, 4, "能用 Chroma/FAISS 做向量检索"),
    (1, 6, 5, "能写 grounded prompt 和拒答规则"),
    (1, 7, 5, "回答必须显示来源证据"),
    (1, 8, 5, "能说明如何降低幻觉"),
    (1, 9, 4, "有可截图的网页 demo"),
    (1, 11, 4, "有测试覆盖关键功能"),
    (1, 12, 4, "GitHub README 能让别人复现"),
    (2, 2, 5, "能解析企业文档"),
    (2, 3, 5, "能展示 chunk 输出"),
    (2, 4, 5, "能生成和查询 embeddings"),
    (2, 5, 5, "能使用向量库"),
    (2, 7, 5, "能引用来源片段"),
    (2, 8, 4, "能拒答无证据问题"),
    (3, 1, 4, "能快速写 demo"),
    (3, 6, 4, "能把业务需求转成 prompt/流程"),
    (3, 9, 5, "有面向用户的页面"),
    (3, 10, 3, "能为 demo 设计结构化数据"),
    (3, 12, 4, "有项目说明和截图"),
    (3, 16, 3, "能用环境变量和依赖文件配置项目"),
    (4, 1, 4, "能读取和分析表格"),
    (4, 10, 4, "能设计数据表或查询"),
    (4, 14, 5, "能用自然语言解释数据"),
    (4, 9, 3, "能做上传和可视化页面"),
    (5, 13, 5, "能组织多步骤工具调用"),
    (5, 15, 5, "能抽取和整理网页来源"),
    (5, 6, 4, "能生成结构化报告"),
    (5, 7, 4, "报告必须保留来源链接"),
]

PROJECTS = [
    (1, "AI 岗位 JD 知识库", "MVP 可运行", "Python, Streamlit, SQLite, TF-IDF", "证明 RAG 流程、来源引用、拒答和数据库查询能力。", "接入 embeddings + Chroma/FAISS。"),
    (2, "Chat with PDF / Basic RAG", "进行中", "Python, pypdf, LangChain", "证明 PDF 读取、文本切分、检索和回答链路。", "完成向量检索和 LLM 回答。"),
    (3, "数据分析 Agent", "待开始", "Python, Pandas, Matplotlib, Streamlit", "证明面向业务数据的自然语言分析能力。", "准备一份模拟销售/运营 CSV。"),
    (4, "Web Research Agent", "待开始", "Python, Search API, Markdown Report", "证明搜索、抽取、去重和报告生成能力。", "先做一个竞品研究报告生成器。"),
    (5, "Agentic RAG 优化", "待开始", "RAG, Query Rewrite, Evaluation", "证明查询改写、低置信度拒答和质量评估能力。", "增加评估集和错误案例复盘。"),
]

PROJECT_SKILLS = [
    (1, 1, "已实现 CLI 和 Streamlit 入口"),
    (1, 2, "已读取 Markdown/PDF 来源"),
    (1, 3, "已实现 chunk + overlap"),
    (1, 7, "已展示来源片段、相关度、命中词"),
    (1, 8, "已实现低分拒答"),
    (1, 9, "已实现中文页面"),
    (1, 10, "本次新增模拟业务数据库"),
    (1, 11, "已有单元测试"),
    (1, 12, "README 已加入截图"),
    (2, 1, "已有 PDF 读取脚本"),
    (2, 2, "已验证示例 PDF 读取"),
    (2, 3, "由知识库 MVP 覆盖基础版本"),
    (3, 14, "待补数据集和图表"),
    (4, 13, "待补工具调用流程"),
    (4, 15, "待补网页抽取"),
    (5, 8, "已有低置信度拒答雏形"),
]

INTERVIEW_QUESTIONS = [
    (1, 3, "基础", "为什么 RAG 项目要先做文本切分？", "长文档不能直接塞进上下文，chunk 让检索更精准，也方便展示来源。"),
    (2, 4, "基础", "Embedding 和关键词检索有什么区别？", "关键词检索看词面匹配，embedding 更关注语义相似度。"),
    (3, 5, "进阶", "为什么要用向量数据库？", "向量库能保存 embedding 并高效检索相似片段，适合文档问答。"),
    (4, 8, "进阶", "如何降低文档问答系统的幻觉？", "只基于检索片段回答、显示来源、低置信度拒答、维护评估集。"),
    (5, 9, "基础", "为什么作品集项目需要网页 demo？", "非技术面试官能直接理解项目价值，也方便截图展示。"),
    (6, 10, "基础", "为什么这里要加 SQLite 模拟数据库？", "它让岗位、技能、项目、面试题形成可查询关系，体现数据建模能力。"),
    (7, 11, "基础", "你给这个项目写了哪些测试？", "覆盖默认文档加载、技能问题检索、无关问题拒答和数据库查询。"),
    (8, 12, "基础", "GitHub README 应该展示什么？", "问题、功能、架构、运行命令、截图、测试结果和简历 bullet。"),
]

LEARNING_TASKS = [
    (1, 4, "接入 OpenAI embedding", "embedding 查询脚本", 3, "待开始"),
    (2, 5, "替换为 Chroma 或 FAISS", "向量库检索 demo", 4, "待开始"),
    (3, 9, "增加文件上传", "Streamlit 上传入口", 2, "待开始"),
    (4, 11, "补数据库查询测试", "test_career_database.py", 1, "已完成"),
    (5, 10, "设计模拟求职数据库", "SQLite schema + seed data", 2, "已完成"),
    (6, 7, "优化来源卡片", "中文来源证据面板", 1, "已完成"),
    (7, 8, "整理拒答案例", "低置信度测试用例", 1, "已完成"),
    (8, 14, "准备数据分析样例", "CSV 数据集和图表 demo", 4, "待开始"),
]


def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(db_path: Path = DEFAULT_DB_PATH) -> Path:
    connection = connect(db_path)
    try:
        connection.executescript(SCHEMA_SQL)
        connection.executemany("INSERT INTO roles VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ROLES)
        connection.executemany("INSERT INTO skills VALUES (?, ?, ?, ?, ?)", SKILLS)
        connection.executemany("INSERT INTO role_skills VALUES (?, ?, ?, ?)", ROLE_SKILLS)
        connection.executemany("INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?)", PROJECTS)
        connection.executemany("INSERT INTO project_skills VALUES (?, ?, ?)", PROJECT_SKILLS)
        connection.executemany("INSERT INTO interview_questions VALUES (?, ?, ?, ?, ?)", INTERVIEW_QUESTIONS)
        connection.executemany("INSERT INTO learning_tasks VALUES (?, ?, ?, ?, ?, ?)", LEARNING_TASKS)
        connection.commit()
    finally:
        connection.close()
    return db_path


def ensure_database(db_path: Path = DEFAULT_DB_PATH) -> Path:
    if not db_path.exists():
        initialize_database(db_path)
    return db_path


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def query_rows(sql: str, params: tuple[Any, ...] = (), db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    ensure_database(db_path)
    connection = connect(db_path)
    try:
        rows = connection.execute(sql, params).fetchall()
    finally:
        connection.close()
    return rows_to_dicts(rows)


def search_jobs(keyword: str = "", db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    pattern = f"%{keyword.strip()}%"
    return query_rows(
        """
        SELECT id, title, level, company_type, business_scenario, location, salary_range, priority
        FROM roles
        WHERE ? = '%%'
           OR title LIKE ?
           OR company_type LIKE ?
           OR business_scenario LIKE ?
        ORDER BY priority DESC, id ASC
        """,
        (pattern, pattern, pattern, pattern),
        db_path,
    )


def role_skill_matrix(role_id: int = 1, db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    return query_rows(
        """
        SELECT
            r.title AS role,
            s.name AS skill,
            s.category,
            s.target_level,
            rs.importance,
            rs.evidence_required
        FROM role_skills rs
        JOIN roles r ON r.id = rs.role_id
        JOIN skills s ON s.id = rs.skill_id
        WHERE rs.role_id = ?
        ORDER BY rs.importance DESC, s.category, s.name
        """,
        (role_id,),
        db_path,
    )


def project_recommendations(role_id: int = 1, db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    return query_rows(
        """
        SELECT
            p.name,
            p.stage,
            p.stack,
            p.resume_value,
            p.next_step,
            COUNT(ps.skill_id) AS matched_skills,
            ROUND(AVG(rs.importance), 2) AS avg_importance
        FROM projects p
        JOIN project_skills ps ON ps.project_id = p.id
        JOIN role_skills rs ON rs.skill_id = ps.skill_id AND rs.role_id = ?
        GROUP BY p.id
        ORDER BY matched_skills DESC, avg_importance DESC, p.id ASC
        """,
        (role_id,),
        db_path,
    )


def interview_pack(role_id: int = 1, db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    return query_rows(
        """
        SELECT
            s.name AS skill,
            iq.difficulty,
            iq.question,
            iq.strong_answer_hint
        FROM interview_questions iq
        JOIN skills s ON s.id = iq.skill_id
        JOIN role_skills rs ON rs.skill_id = s.id
        WHERE rs.role_id = ?
        ORDER BY rs.importance DESC, iq.id ASC
        """,
        (role_id,),
        db_path,
    )


def learning_plan(status: str = "", db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    pattern = f"%{status.strip()}%"
    return query_rows(
        """
        SELECT
            lt.status,
            s.name AS skill,
            lt.task_name,
            lt.output_artifact,
            lt.estimated_hours
        FROM learning_tasks lt
        JOIN skills s ON s.id = lt.skill_id
        WHERE ? = '%%' OR lt.status LIKE ?
        ORDER BY
            CASE lt.status
                WHEN '进行中' THEN 1
                WHEN '待开始' THEN 2
                WHEN '已完成' THEN 3
                ELSE 4
            END,
            lt.estimated_hours ASC,
            lt.id ASC
        """,
        (pattern, pattern),
        db_path,
    )


def safe_select(sql: str, db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    statement = sql.strip()
    if not statement:
        return []

    lowered = statement.lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise ValueError("只允许执行 SELECT / WITH 只读查询。")
    if ";" in statement.rstrip(";"):
        raise ValueError("一次只能执行一条查询。")

    return query_rows(statement.rstrip(";"), (), db_path)


QUERY_PRESETS = {
    "jobs": ("岗位列表", search_jobs),
    "skills": ("目标岗位技能矩阵", role_skill_matrix),
    "projects": ("项目推荐", project_recommendations),
    "interview": ("面试题包", interview_pack),
    "plan": ("学习任务", learning_plan),
}


def print_table(rows: list[dict[str, Any]]) -> None:
    if not rows:
        print("没有查询到结果。")
        return

    columns = list(rows[0].keys())
    widths = {
        column: min(32, max(len(str(column)), *(len(str(row[column])) for row in rows)))
        for column in columns
    }
    header = " | ".join(column.ljust(widths[column]) for column in columns)
    print(header)
    print("-" * len(header))
    for row in rows:
        print(" | ".join(str(row[column])[: widths[column]].ljust(widths[column]) for column in columns))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="初始化并查询本地 AI 求职演示 SQLite 数据库。")
    parser.add_argument("--init", action="store_true", help="根据种子数据重新创建 SQLite 数据库。")
    parser.add_argument("--query", choices=QUERY_PRESETS.keys(), default="jobs", help="要执行的预设查询。")
    parser.add_argument("--keyword", default="", help="岗位搜索关键词。")
    parser.add_argument("--role-id", type=int, default=1, help="技能、项目或面试题查询使用的岗位编号。")
    parser.add_argument("--status", default="", help="学习任务状态筛选条件。")
    parser.add_argument("--sql", default="", help="执行只读 SELECT 查询。")
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH, help="SQLite 数据库路径。")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    if args.init:
        initialize_database(args.db_path)
        print(f"数据库已初始化：{args.db_path}")

    ensure_database(args.db_path)

    if args.sql:
        rows = safe_select(args.sql, args.db_path)
    elif args.query == "jobs":
        rows = search_jobs(args.keyword, args.db_path)
    elif args.query == "skills":
        rows = role_skill_matrix(args.role_id, args.db_path)
    elif args.query == "projects":
        rows = project_recommendations(args.role_id, args.db_path)
    elif args.query == "interview":
        rows = interview_pack(args.role_id, args.db_path)
    else:
        rows = learning_plan(args.status, args.db_path)

    print_table(rows)


if __name__ == "__main__":
    main()
