import { PageHeader } from "../../components/candidate-shell";

const layers = [
  ["Legacy estate", "Java", "Maps LegacyTransaction to the canonical batch contract. No DQ or finance judgement."],
  ["Domain engine", "Python", "Owns validation, deduplication, quarantine, reconciliation, idempotency and readiness."],
  ["Evidence storage", "Azure Blob / Azurite", "Persists raw, processed, quarantine and audit evidence behind a storage abstraction."],
  ["Cloud contract", "Terraform", "Declares RG, StorageV2, private containers, Linux Y1 and Python 3.12 Function App. No apply claim."],
  ["Operations", "MCP", "Six read-only tools expose deterministic persisted evidence to operators and AI assistants."],
  ["Finance controls", "Decimal invariants", "Accepted-only control totals and exact €0.00 reconciliation difference."],
] as const;

export default function ArchitecturePage() {
  return (
    <div className="demo-grid">
      <PageHeader
        eyebrow="ARCHITECTURE · OWNERSHIP BOUNDARIES"
        title="Modernize the bridge, not the entire estate"
        lede="FinBridge connects a legacy finance source to a modern cloud-compatible evidence pipeline while keeping domain decisions deterministic and explicit."
      />
      <section className="panel architecture-flow">
        {layers.map(([label, tech, body]) => (
          <article key={label} className="arch-card">
            <div className="eyebrow">{label}</div>
            <h2>{tech}</h2>
            <p className="muted">{body}</p>
          </article>
        ))}
      </section>
      <section className="panel">
        <div className="eyebrow">GOLDEN FLOW</div>
        <p className="flow-line">Java legacy → canonical CSV → Python → Blob/Azurite → QUALITY_BLOCKED → quarantine → reconciliation → replay → READY_FOR_ANALYTICS → MCP explanation</p>
      </section>
    </div>
  );
}
