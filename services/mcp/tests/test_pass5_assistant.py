from __future__ import annotations

import unittest

from finbridge_domain.contracts import FROZEN_SCENARIO
from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_mcp import ControlledOperationsAssistant, OperationsService, ToolCallError
from finbridge_processing import ProcessingOrchestrator
from finbridge_storage import build_in_memory_storage


class Pass5ControlledAssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        storage = build_in_memory_storage()
        ProcessingOrchestrator(storage).run_golden_path(build_synthetic_legacy_batch())
        self.assistant = ControlledOperationsAssistant(OperationsService(storage))
        self.batch_id = FROZEN_SCENARIO.batch_id

    def test_why_blocked_uses_exact_three_evidence_tools_without_llm(self) -> None:
        response = self.assistant.answer(self.batch_id, "Why was this batch initially blocked?")
        self.assertEqual(
            response.evidence_used,
            ("get_data_quality_summary", "list_batch_anomalies", "get_reconciliation_result"),
        )
        self.assertIn("3 duplicate records", response.answer)
        self.assertIn("2 invalid-currency records", response.answer)
        self.assertIs(response.deterministic, True)
        self.assertIs(response.live_llm_used, False)

    def test_analytics_answer_does_not_claim_ai_made_decision(self) -> None:
        response = self.assistant.answer(self.batch_id, "Is this batch safe for analytics?")
        self.assertTrue(response.answer.startswith("Yes."))
        self.assertIn("did not make the finance decision", response.answer)

    def test_transaction_explanation_names_dq_owner(self) -> None:
        response = self.assistant.answer(self.batch_id, "What happened to transaction TX-01011?")
        self.assertIn("DQ-02", response.answer)
        self.assertIn("not from AI", response.answer)

    def test_unknown_prompt_has_no_live_llm_fallback(self) -> None:
        with self.assertRaises(ToolCallError):
            self.assistant.answer(self.batch_id, "Predict next month's banking losses")


if __name__ == "__main__":
    unittest.main()
