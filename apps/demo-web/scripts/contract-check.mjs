import fs from "node:fs";
import path from "node:path";

const cwd = process.cwd();
const read = (p) => fs.readFileSync(path.join(cwd, p), "utf8");
const required = [
  "app/page.tsx",
  "app/quality/page.tsx",
  "app/operations/page.tsx",
  "app/architecture/page.tsx",
  "app/candidate/page.tsx",
  "components/candidate-shell.tsx",
  "components/golden-demo.tsx",
  "data/candidate-evidence.ts",
];
for (const file of required) {
  if (!fs.existsSync(path.join(cwd, file))) throw new Error(`PASS 7 route/source missing: ${file}`);
}
const shell = read("components/candidate-shell.tsx");
const evidence = read("data/candidate-evidence.ts");
const operations = read("app/operations/page.tsx");
const candidate = read("app/candidate/page.tsx");
const pipeline = read("components/golden-demo.tsx");
const data = JSON.parse(read("data/golden-path.json"));

for (const href of ["/quality", "/operations", "/architecture", "/candidate"]) {
  if (!shell.includes(href)) throw new Error(`Shared navigation missing ${href}`);
}
if (!evidence.includes("AlpineBank is fictional")) throw new Error("Synthetic disclaimer missing");
if (!pipeline.includes("Inspect 5 anomalies")) throw new Error("Pipeline anomaly inspection missing");
for (const tool of [
  "get_batch_status",
  "get_data_quality_summary",
  "list_batch_anomalies",
  "trace_transaction",
  "get_reconciliation_result",
  "explain_quarantined_record",
]) {
  if (!evidence.includes(tool)) throw new Error(`Frozen MCP tool missing: ${tool}`);
}
if (!operations.includes("evidenceUsed")) throw new Error("AI Operations must expose evidence_used provenance");
if (!candidate.includes("nonClaims")) throw new Error("Candidate route must carry explicit non-claims");

const blocked = data.stages.find((stage) => stage.state === "QUALITY_BLOCKED");
const ready = data.stages.find((stage) => stage.state === "READY_FOR_ANALYTICS");
if (!blocked || !ready) throw new Error("Golden path JSON is incomplete");
if (blocked.accepted_records !== 1019 || blocked.anomaly_records !== 5) throw new Error("Frozen quality evidence changed");
if (ready.unaccounted_records !== 0) throw new Error("Final accountability must be exact");
if (ready.reconciliation?.difference_eur !== "0.00") throw new Error("Reconciliation must be exact");
if (ready.replay?.new_accepted_records !== 0 || ready.replay?.duplicate_imports !== 0 || ready.replay?.additional_quarantine_rows !== 0) {
  throw new Error("Replay must remain 0/0/0");
}
console.log("PASS 7 frontend candidate-experience contract: PASS");
