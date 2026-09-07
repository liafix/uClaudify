import { PageHeader } from "../../components/candidate-shell";
import { evidenceUsed, mcpTools } from "../../data/candidate-evidence";

export default function OperationsPage() {
  return (
    <div className="demo-grid">
      <PageHeader
        eyebrow="AI OPERATIONS · READ ONLY"
        title="Explain evidence without giving AI decision authority"
        lede="Six MCP tools expose persisted batch evidence. The controlled assistant can explain why a batch was blocked, but cannot mutate storage, run SQL or bypass the quality gate."
      />
      <section className="panel">
        <div className="eyebrow">OFFICIAL MCP SDK VERIFIED</div>
        <h2>Exactly six closed-world tools</h2>
        <div className="tool-grid">
          {mcpTools.map((tool) => <code className="tool" key={tool}>{tool}</code>)}
        </div>
        <p className="muted">All six are read-only and were runtime-validated through the official MCP Python SDK v2 client in PASS 5.</p>
      </section>
      <section className="panel assistant-answer">
        <div className="eyebrow">CONTROLLED AI OPERATIONS EVIDENCE</div>
        <h2>Why was this batch initially blocked?</h2>
        <p>Because deterministic quality checks found <b>3 duplicate records</b> and <b>2 invalid-currency records</b>. The pipeline accepted 1,019 records, quarantined 5, and then reconciled to an exact <b>€0.00</b> difference before reaching analytics readiness.</p>
        <div className="evidence-strip">
          <span>evidence_used</span>
          {evidenceUsed.map((tool) => <code key={tool}>{tool}</code>)}
        </div>
      </section>
    </div>
  );
}
