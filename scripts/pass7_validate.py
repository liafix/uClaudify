#!/usr/bin/env python3
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
web = root / "apps" / "demo-web"
required = [
    web / "app" / "page.tsx",
    web / "app" / "quality" / "page.tsx",
    web / "app" / "operations" / "page.tsx",
    web / "app" / "architecture" / "page.tsx",
    web / "app" / "candidate" / "page.tsx",
    web / "components" / "candidate-shell.tsx",
    web / "data" / "candidate-evidence.ts",
]
for path in required:
    assert path.exists(), f"missing PASS 7 source: {path.relative_to(root)}"
current_pass = int((root / "contracts" / "current_pass.txt").read_text().strip())
assert current_pass >= 7
text = "\n".join(path.read_text() for path in required)
for token in ["Python", "Java", "Azure", "Terraform", "MCP", "QUALITY_BLOCKED", "READY_FOR_ANALYTICS"]:
    assert token in text, f"candidate evidence mapping missing {token}"
for tool in [
    "get_batch_status", "get_data_quality_summary", "list_batch_anomalies",
    "trace_transaction", "get_reconciliation_result", "explain_quarantined_record",
]:
    assert tool in text, f"MCP tool missing: {tool}"
assert "AlpineBank is fictional" in text
assert "terraform apply" in text.lower()
# The phrase must exist only as an explicit non-claim/boundary, never as an execution claim.
assert "No terraform apply" in text or "no terraform apply" in text

data=json.loads((web/'data'/'golden-path.json').read_text())
blocked=next(s for s in data['stages'] if s['state']=='QUALITY_BLOCKED')
ready=next(s for s in data['stages'] if s['state']=='READY_FOR_ANALYTICS')
assert blocked['input_records']==1024 and blocked['accepted_records']==1019 and blocked['anomaly_records']==5
assert ready['quarantined_records']==5 and ready['unaccounted_records']==0
assert ready['reconciliation']['difference_eur']=='0.00'
assert ready['replay']['new_accepted_records']==0
assert ready['replay']['duplicate_imports']==0
assert ready['replay']['additional_quarantine_rows']==0
# PASS 7 scope-stop is enforced only while PASS 7 is the current pass.
if current_pass == 7:
    assert not (root / "scripts" / "pass8_gate.sh").exists()
else:
    assert (root / "scripts" / "pass8_gate.sh").exists()
print("PASS 7 structural candidate-experience validation: PASS")
