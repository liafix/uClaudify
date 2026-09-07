"""Deterministic operations-assistant evidence for PASS 5.

This is deliberately not a live LLM. It demonstrates the control pattern that a future model would
use: select approved read-only tools, receive structured evidence and produce a bounded explanation
with explicit `evidence_used`. The deterministic adapter keeps the candidate golden path API-key
free and reviewable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .operations import OperationsService, ToolCallError


@dataclass(frozen=True, slots=True)
class AssistantResponse:
    question: str
    answer: str
    evidence_used: tuple[str, ...]
    evidence: tuple[Mapping[str, object], ...]
    deterministic: bool = True
    live_llm_used: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "question": self.question,
            "answer": self.answer,
            "evidence_used": list(self.evidence_used),
            "evidence": [dict(item) for item in self.evidence],
            "deterministic": self.deterministic,
            "live_llm_used": self.live_llm_used,
        }


class ControlledOperationsAssistant:
    """Bounded deterministic explanation layer over the six approved MCP tools."""

    def __init__(self, operations: OperationsService) -> None:
        self._operations = operations

    def answer(self, batch_id: str, question: str) -> AssistantResponse:
        normalized = " ".join(question.lower().strip().split())
        if normalized in {
            "why was this batch initially blocked?",
            "why was the batch initially blocked?",
        }:
            quality = self._operations.get_data_quality_summary(batch_id)
            anomalies = self._operations.list_batch_anomalies(batch_id)
            recon = self._operations.get_reconciliation_result(batch_id)
            rules = quality["issues_by_rule"]
            assert isinstance(rules, dict)
            answer = (
                f"Batch {batch_id} was initially blocked by deterministic data-quality rules: "
                f"{rules.get('DQ-01', 0)} duplicate records and {rules.get('DQ-02', 0)} invalid-"
                f"currency records were quarantined. {quality['accepted_records']} records were "
                f"accepted, {quality['quarantined_records']} were quarantined, and reconciliation "
                f"later completed with an exact EUR difference of {recon['difference_eur']}."
            )
            return AssistantResponse(
                question,
                answer,
                (
                    "get_data_quality_summary",
                    "list_batch_anomalies",
                    "get_reconciliation_result",
                ),
                (quality, anomalies, recon),
            )

        if normalized in {
            "is this batch safe for analytics?",
            "is the batch ready for analytics?",
        }:
            status = self._operations.get_batch_status(batch_id)
            quality = self._operations.get_data_quality_summary(batch_id)
            recon = self._operations.get_reconciliation_result(batch_id)
            ready = (
                status["current_state"] == "READY_FOR_ANALYTICS"
                and quality["unaccounted_records"] == 0
                and recon["reconciled"] is True
            )
            answer = (
                f"{'Yes' if ready else 'No'}. Persisted evidence reports state "
                f"{status['current_state']}, {quality['unaccounted_records']} unaccounted records, "
                f"and reconciliation difference {recon['difference_eur']} EUR. The assistant did "
                "not make the finance decision; it only summarized deterministic pipeline evidence."
            )
            return AssistantResponse(
                question,
                answer,
                ("get_batch_status", "get_data_quality_summary", "get_reconciliation_result"),
                (status, quality, recon),
            )

        prefix = "what happened to transaction "
        if normalized.startswith(prefix) and normalized.endswith("?"):
            transaction_id = question.strip().rstrip("?").split()[-1]
            trace = self._operations.trace_transaction(batch_id, transaction_id)
            evidence_used = ["trace_transaction"]
            evidence: list[Mapping[str, object]] = [trace]
            if trace["outcome"] == "QUARANTINED":
                explanation = self._operations.explain_quarantined_record(batch_id, transaction_id)
                evidence_used.append("explain_quarantined_record")
                evidence.append(explanation)
                details = explanation["explanation"]
                assert isinstance(details, list) and details
                first = details[0]
                assert isinstance(first, dict)
                answer = (
                    f"{transaction_id} was quarantined by {first['rule']} because "
                    f"{first['reason']}. The decision came from the Python deterministic DQ engine, "
                    "not from AI."
                )
            else:
                answer = f"{transaction_id} was accepted into the verified dataset with no quarantine issue."
            return AssistantResponse(question, answer, tuple(evidence_used), tuple(evidence))

        raise ToolCallError(
            "Deterministic assistant supports only the frozen PASS 5 demo questions; no live LLM fallback is enabled"
        )
