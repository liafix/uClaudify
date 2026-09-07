import { PageHeader } from "../../components/candidate-shell";
import { anomalies, goldenFacts } from "../../data/candidate-evidence";

export default function QualityPage() {
  return (
    <div className="demo-grid">
      <PageHeader
        eyebrow="QUALITY · PYTHON DOMAIN OWNER"
        title="Pipeline success is not data trust"
        lede="FinBridge blocks the batch until every anomaly has an explicit outcome, then reconciles only the accepted records with exact Decimal finance controls."
      />
      <section className="panel">
        <div className="metric-grid">
          <article><span>Input</span><strong>{goldenFacts.input}</strong></article>
          <article><span>Accepted</span><strong>{goldenFacts.accepted}</strong></article>
          <article><span>Quarantined</span><strong>{goldenFacts.quarantined}</strong></article>
          <article><span>Unaccounted</span><strong>{goldenFacts.unaccounted}</strong></article>
          <article><span>Accountability</span><strong>{goldenFacts.accountability}</strong></article>
        </div>
      </section>
      <section className="panel">
        <div className="eyebrow">DQ-01 + DQ-02 EVIDENCE</div>
        <h2>Five anomalies, zero silent loss</h2>
        <div className="anomaly-list">
          {anomalies.map((item) => (
            <article key={item.id}>
              <div><strong>{item.id}</strong><span>deterministic source evidence</span></div>
              <code>{item.rule}</code>
              <p>{item.reason}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="panel split-panel">
        <div>
          <div className="eyebrow">FINANCIAL RECONCILIATION</div>
          <h2>Exact closing balance</h2>
          <p className="muted">Only the 1,019 accepted records participate in reconciliation.</p>
        </div>
        <div className="recon-grid">
          <span>Opening <b>{goldenFacts.opening}</b></span>
          <span>Credits <b>{goldenFacts.credits}</b></span>
          <span>Debits <b>{goldenFacts.debits}</b></span>
          <span>Expected closing <b>{goldenFacts.expectedClosing}</b></span>
          <span>Calculated closing <b>{goldenFacts.calculatedClosing}</b></span>
          <span className="difference">Difference <b>{goldenFacts.difference}</b></span>
        </div>
      </section>
    </div>
  );
}
