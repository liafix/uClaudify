"use client";

import { useMemo, useState } from "react";

type Issue = {
  transaction_id: string;
  source_line: number;
  rule: string;
  reason: string;
};

type Reconciliation = {
  opening_balance_eur: string;
  credits_eur: string;
  debits_eur: string;
  expected_closing_balance_eur: string;
  calculated_closing_balance_eur: string;
  difference_eur: string;
  reconciled: boolean;
};

type Replay = {
  batch_id: string;
  previously_processed: boolean;
  new_accepted_records: number;
  duplicate_imports: number;
  additional_quarantine_rows: number;
};

type Stage = {
  state: string;
  input_records: number;
  accepted_records: number;
  anomaly_records: number;
  quarantined_records: number;
  unaccounted_records: number;
  issues: Issue[];
  reconciliation?: Reconciliation;
  replay?: Replay;
};

type GoldenPath = {
  batch_id: string;
  source_system: string;
  synthetic: boolean;
  stages: Stage[];
  state_history: string[];
};

const buttonLabels = [
  "Process Daily Batch",
  "Quarantine Invalid Records",
  "Run Reconciliation",
  "Replay Batch",
  "Confirm Analytics Readiness",
];

function euros(value: string | undefined) {
  if (!value) return "—";
  return new Intl.NumberFormat("en-IE", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
  }).format(Number(value));
}

export function GoldenDemo({ data }: { data: GoldenPath }) {
  const [stageIndex, setStageIndex] = useState(0);
  const [showAnomalies, setShowAnomalies] = useState(false);
  const stage = data.stages[stageIndex];
  const isReady = stage.state === "READY_FOR_ANALYTICS";
  const canInspect = stage.state === "QUALITY_BLOCKED";

  const visibleHistory = useMemo(() => {
    const currentIndex = data.state_history.indexOf(stage.state);
    return data.state_history.slice(0, currentIndex + 1);
  }, [data.state_history, stage.state]);

  function advance() {
    setShowAnomalies(false);
    setStageIndex((current) => Math.min(current + 1, data.stages.length - 1));
  }

  function reset() {
    setStageIndex(0);
    setShowAnomalies(false);
  }

  return (
    <div className="demo-grid">
      <section className="panel hero-panel">
        <div className="eyebrow">GOLDEN VERTICAL SLICE · PASS 1</div>
        <div className="hero-row">
          <div>
            <h1>FinBridge Cloud</h1>
            <p className="lede">
              Legacy finance input → Python quality gate → quarantine → reconciliation → idempotent
              replay → analytics-ready data.
            </p>
          </div>
          <div className={`status ${isReady ? "status-ready" : canInspect ? "status-blocked" : ""}`}>
            <span>Current state</span>
            <strong>{stage.state.replaceAll("_", " ")}</strong>
          </div>
        </div>
        <div className="meta-row">
          <span>Batch <b>{data.batch_id}</b></span>
          <span>Source <b>{data.source_system}</b></span>
          <span>Mode <b>synthetic / deterministic</b></span>
        </div>
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <div className="eyebrow">PIPELINE EVIDENCE</div>
            <h2>Trust the data, not just the successful job</h2>
          </div>
          <div className="actions">
            {canInspect && (
              <button className="button secondary" onClick={() => setShowAnomalies((value) => !value)}>
                {showAnomalies ? "Hide anomalies" : "Inspect 5 anomalies"}
              </button>
            )}
            {!isReady ? (
              <button className="button" onClick={advance}>
                {buttonLabels[stageIndex]}
              </button>
            ) : (
              <button className="button secondary" onClick={reset}>Reset demo</button>
            )}
          </div>
        </div>

        <div className="metric-grid">
          <article><span>Input</span><strong>{stage.input_records.toLocaleString()}</strong></article>
          <article><span>Accepted</span><strong>{stage.accepted_records.toLocaleString()}</strong></article>
          <article><span>Anomalies</span><strong>{stage.anomaly_records}</strong></article>
          <article><span>Quarantined</span><strong>{stage.quarantined_records}</strong></article>
          <article><span>Unaccounted</span><strong>{stage.unaccounted_records.toLocaleString()}</strong></article>
        </div>

        <div className="timeline">
          {data.state_history.map((item) => {
            const reached = visibleHistory.includes(item);
            const current = item === stage.state;
            return (
              <div className={`timeline-item ${reached ? "reached" : ""} ${current ? "current" : ""}`} key={item}>
                <span className="dot" />
                <span>{item.replaceAll("_", " ")}</span>
              </div>
            );
          })}
        </div>
      </section>

      {canInspect && showAnomalies && (
        <section className="panel">
          <div className="eyebrow">QUALITY GATE · BLOCKED</div>
          <h2>Five records need an explicit outcome</h2>
          <div className="anomaly-list">
            {stage.issues.map((issue) => (
              <article key={`${issue.transaction_id}-${issue.source_line}`}>
                <div><strong>{issue.transaction_id}</strong><span>source line {issue.source_line}</span></div>
                <code>{issue.rule}</code>
                <p>{issue.reason}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {stage.reconciliation && (
        <section className="panel split-panel">
          <div>
            <div className="eyebrow">FINANCIAL RECONCILIATION</div>
            <h2>{stage.reconciliation.reconciled ? "Exact control total" : "Reconciliation failed"}</h2>
            <p className="muted">Only accepted records participate in the control total.</p>
          </div>
          <div className="recon-grid">
            <span>Opening <b>{euros(stage.reconciliation.opening_balance_eur)}</b></span>
            <span>Credits <b>{euros(stage.reconciliation.credits_eur)}</b></span>
            <span>Debits <b>{euros(stage.reconciliation.debits_eur)}</b></span>
            <span>Expected closing <b>{euros(stage.reconciliation.expected_closing_balance_eur)}</b></span>
            <span>Calculated closing <b>{euros(stage.reconciliation.calculated_closing_balance_eur)}</b></span>
            <span className="difference">Difference <b>{euros(stage.reconciliation.difference_eur)}</b></span>
          </div>
        </section>
      )}

      {stage.replay && (
        <section className="panel">
          <div className="eyebrow">IDEMPOTENCY EVIDENCE</div>
          <h2>Replay creates no second dataset</h2>
          <div className="metric-grid three">
            <article><span>New accepted records</span><strong>{stage.replay.new_accepted_records}</strong></article>
            <article><span>Duplicate imports</span><strong>{stage.replay.duplicate_imports}</strong></article>
            <article><span>Additional quarantine</span><strong>{stage.replay.additional_quarantine_rows}</strong></article>
          </div>
        </section>
      )}

      <section className="panel disclaimer">
        <strong>Independent synthetic candidate demonstration.</strong>
        <p>
          AlpineBank is fictional. No uCloudify client data, internal repositories, proprietary
          architecture, production credentials, or confidential processes are represented or used.
        </p>
      </section>
    </div>
  );
}
