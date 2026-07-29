from __future__ import annotations

import unittest

from jd_knowledge_base import DEFAULT_SOURCE_PATHS, KnowledgeBase, answer_question, load_documents


class JobDescriptionKnowledgeBaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.documents = load_documents(DEFAULT_SOURCE_PATHS)
        cls.knowledge_base = KnowledgeBase.from_documents(cls.documents)

    def test_loads_default_documents(self) -> None:
        self.assertGreaterEqual(len(self.documents), 4)
        self.assertGreater(len(self.knowledge_base.chunks), 4)

    def test_retrieves_required_skills(self) -> None:
        results = self.knowledge_base.retrieve("这个岗位要求哪些技能？", top_k=3)
        self.assertTrue(results)
        answer = answer_question("这个岗位要求哪些技能？", results)
        self.assertIn("来源：", answer)
        self.assertIn("Python", answer)
        self.assertIn("文本切分", answer)

    def test_refuses_when_evidence_is_missing(self) -> None:
        results = self.knowledge_base.retrieve("木星风暴如何制作咖啡？", top_k=3)
        answer = answer_question("木星风暴如何制作咖啡？", results)
        self.assertIn("当前知识库没有足够证据", answer)


if __name__ == "__main__":
    unittest.main()
