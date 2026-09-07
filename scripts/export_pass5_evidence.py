#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for relative in ("services/domain", "services/storage", "services/processing", "services/mcp"):
    sys.path.insert(0, str(ROOT / relative))

from finbridge_domain.contracts import FROZEN_SCENARIO  # noqa: E402
from finbridge_domain.fixtures import build_synthetic_legacy_batch  # noqa: E402
from finbridge_mcp import ControlledOperationsAssistant, OperationsService  # noqa: E402
from finbridge_processing import ProcessingOrchestrator  # noqa: E402
from finbridge_storage import build_in_memory_storage  # noqa: E402

storage = build_in_memory_storage()
ProcessingOrchestrator(storage).run_golden_path(build_synthetic_legacy_batch())
ops = OperationsService(storage)
assistant = ControlledOperationsAssistant(ops)
batch_id = FROZEN_SCENARIO.batch_id
payload = {
    "synthetic": True,
    "batch_id": batch_id,
    "mcp_tools": [spec.as_mcp_dict() for spec in ops.tool_specs],
    "questions": [
        assistant.answer(batch_id, "Why was this batch initially blocked?").as_dict(),
        assistant.answer(batch_id, "Is this batch safe for analytics?").as_dict(),
        assistant.answer(batch_id, "What happened to transaction TX-01011?").as_dict(),
    ],
    "safety": {
        "read_only": True,
        "live_llm_dependency": False,
        "arbitrary_sql": False,
        "arbitrary_shell": False,
        "ai_is_finance_decision_owner": False,
    },
}
out = ROOT / "artifacts/pass5/ai-operations-evidence.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
print(out)
