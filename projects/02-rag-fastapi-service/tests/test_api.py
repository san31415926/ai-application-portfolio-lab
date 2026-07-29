import os
import unittest

os.environ.setdefault("RAG_EMBEDDING_BACKEND", "sparse")
os.environ.setdefault("RAG_MIN_SCORE", "0.045")
os.environ.setdefault("RAG_GENERATION_BACKEND", "extractive")

from fastapi.testclient import TestClient

from app.main import app
from app.services.answer_generator import OllamaAnswerGenerator
from app.services.note_service import note_service
from app.services.rag_service import rag_service


class RagFastApiServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        rag_service.clear()
        note_service.clear()
        self.client = TestClient(app)

    def test_health_check(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

        app_response = self.client.get("/app/")
        self.assertEqual(app_response.status_code, 200)
        self.assertIn("LearningHub", app_response.text)
        self.assertNotIn("简历项目", app_response.text)
        self.assertNotIn("把做菜", app_response.text)
        self.assertNotIn("OpenAPI", app_response.text)
        self.assertNotIn("Health", app_response.text)
        self.assertNotIn("样例", app_response.text)

    def test_chat_model_listing_contract(self) -> None:
        response = self.client.get("/api/v1/models")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIn("models", payload["data"])
        self.assertIn("default_model", payload["data"])

    def test_sample_index_and_query(self) -> None:
        load_response = self.client.post("/api/v1/knowledge/documents/samples")
        self.assertEqual(load_response.status_code, 200)
        self.assertGreaterEqual(len(load_response.json()["data"]), 4)

        duplicate_response = self.client.post("/api/v1/knowledge/documents/samples")
        self.assertEqual(duplicate_response.status_code, 200)
        self.assertEqual(len(duplicate_response.json()["data"]), 0)

        stats_response = self.client.get("/api/v1/knowledge/stats")
        self.assertEqual(stats_response.status_code, 200)
        self.assertGreaterEqual(stats_response.json()["data"]["chunk_count"], 4)

        query_response = self.client.post(
            "/api/v1/chat/query",
            json={"query": "C 语言中的变量怎么理解？", "top_k": 3},
        )
        payload = query_response.json()

        self.assertEqual(query_response.status_code, 200)
        self.assertFalse(payload["refused"])
        self.assertGreaterEqual(payload["hit_count"], 1)
        self.assertIn("变量是给数据起名字", payload["answer"])
        self.assertEqual(payload["sources"][0]["filename"], "c_language_basics_zh.md")
        self.assertEqual(payload["answer_backend"], "extractive")

        chinese_query_response = self.client.post(
            "/api/v1/chat/query",
            json={"query": "番茄炒蛋怎么做？", "top_k": 3},
        )
        chinese_payload = chinese_query_response.json()

        self.assertEqual(chinese_query_response.status_code, 200)
        self.assertFalse(chinese_payload["refused"])
        self.assertIn("番茄", chinese_payload["answer"])
        self.assertEqual(chinese_payload["sources"][0]["filename"], "cooking_tomato_egg_zh.md")

    def test_upload_document_and_list_chunks(self) -> None:
        response = self.client.post(
            "/api/v1/knowledge/documents/upload",
            files={"file": ("algorithm.txt", b"Binary search requires sorted data and halves the search range.", "text/plain")},
        )
        self.assertEqual(response.status_code, 200)
        document_id = response.json()["data"]["document_id"]

        list_response = self.client.get("/api/v1/knowledge/documents")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()["data"][0]["filename"], "algorithm.txt")

        chunk_response = self.client.get(f"/api/v1/knowledge/documents/{document_id}/chunks")
        self.assertEqual(chunk_response.status_code, 200)
        self.assertIn("Binary search", chunk_response.json()["data"][0]["content"])

    def test_refuse_when_no_evidence(self) -> None:
        self.client.post("/api/v1/knowledge/documents/samples")
        response = self.client.post(
            "/api/v1/chat/query",
            json={"query": "How to register a quantum treaty on Mars?", "top_k": 3, "min_score": 0.2},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["refused"])

    def test_sample_notes_import_tutorial_library_once(self) -> None:
        response = self.client.post("/api/v1/notes/samples")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 205)
        self.assertTrue(any("Docker" in note["title"] for note in response.json()["data"]))

        duplicate_response = self.client.post("/api/v1/notes/samples")
        self.assertEqual(duplicate_response.status_code, 200)
        self.assertEqual(len(duplicate_response.json()["data"]), 0)

        stats_response = self.client.get("/api/v1/notes/stats")
        self.assertEqual(stats_response.status_code, 200)
        self.assertEqual(stats_response.json()["data"]["note_count"], 205)

    def test_notebook_notes_and_related_sources(self) -> None:
        self.client.post("/api/v1/knowledge/documents/samples")

        note_response = self.client.post(
            "/api/v1/notes",
            json={
                "title": "C 语言变量学习笔记",
                "content": "变量是给数据起名字的一种方式，C 语言里常见类型包括 int、double 和 char。",
                "tags": ["C语言", "变量"],
                "category": "编程学习",
            },
        )
        self.assertEqual(note_response.status_code, 200)
        note_id = note_response.json()["data"]["note_id"]

        related_response = self.client.get(f"/api/v1/notes/{note_id}/related?top_k=3")
        self.assertEqual(related_response.status_code, 200)
        self.assertEqual(related_response.json()["data"][0]["filename"], "c_language_basics_zh.md")

        assist_response = self.client.post(f"/api/v1/notes/{note_id}/assist", json={"mode": "summary"})
        self.assertEqual(assist_response.status_code, 200)
        self.assertIn("变量是给数据起名字", assist_response.json()["data"]["result"])

        search_response = self.client.post("/api/v1/notes/search", json={"query": "C语言变量", "top_k": 3})
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.json()["data"][0]["note_id"], note_id)

    def test_writing_assist_uses_local_chat_generator(self) -> None:
        note_response = self.client.post(
            "/api/v1/notes",
            json={
                "title": "Embedding 学习笔记",
                "content": "Embedding 可以把文本转换成向量，用于相似度检索。",
                "tags": ["Embedding", "RAG"],
                "category": "AI 学习",
            },
        )
        note_id = note_response.json()["data"]["note_id"]

        class StubGenerator:
            model_name = "qwen2.5:3b"

            @staticmethod
            def generate_writing_assist(mode, title, content, sources):
                return f"模型生成：{mode}：{title}"

        previous_generator = rag_service.answer_generator
        rag_service.answer_generator = StubGenerator()
        try:
            response = self.client.post(
                f"/api/v1/notes/{note_id}/assist",
                json={"mode": "summary"},
            )
        finally:
            rag_service.answer_generator = previous_generator

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["answer_backend"], "ollama")
        self.assertEqual(response.json()["data"]["answer_model"], "qwen2.5:3b")
        self.assertIn("模型生成", response.json()["data"]["result"])

    def test_qwen_reasoning_cleanup(self) -> None:
        raw = "<think>内部分析</think>\n最终答案：变量是给数据起名字的方式。\n\n后续分析"
        self.assertEqual(
            OllamaAnswerGenerator._extract_final_answer(raw),
            "变量是给数据起名字的方式。",
        )


if __name__ == "__main__":
    unittest.main()
