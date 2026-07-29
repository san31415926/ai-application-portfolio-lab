from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from career_database import (
    initialize_database,
    interview_pack,
    learning_plan,
    project_recommendations,
    role_skill_matrix,
    safe_select,
    search_jobs,
)


class CareerDatabaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "career.sqlite"
        initialize_database(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_search_jobs_returns_ai_roles(self) -> None:
        rows = search_jobs("RAG", self.db_path)
        self.assertTrue(rows)
        self.assertIn("RAG", rows[0]["business_scenario"] + rows[0]["title"])

    def test_role_skill_matrix_contains_source_citation(self) -> None:
        rows = role_skill_matrix(1, self.db_path)
        skill_names = {row["skill"] for row in rows}
        self.assertIn("来源引用", skill_names)
        self.assertIn("低置信度拒答", skill_names)

    def test_project_recommendations_rank_current_project(self) -> None:
        rows = project_recommendations(1, self.db_path)
        self.assertEqual(rows[0]["name"], "AI 岗位 JD 知识库")
        self.assertGreaterEqual(rows[0]["matched_skills"], 6)

    def test_interview_and_learning_queries_have_outputs(self) -> None:
        self.assertTrue(interview_pack(1, self.db_path))
        self.assertTrue(learning_plan("待开始", self.db_path))

    def test_safe_select_allows_only_read_queries(self) -> None:
        rows = safe_select("SELECT name, category FROM skills ORDER BY id LIMIT 3", self.db_path)
        self.assertEqual(len(rows), 3)
        with self.assertRaises(ValueError):
            safe_select("DELETE FROM skills", self.db_path)


if __name__ == "__main__":
    unittest.main()
