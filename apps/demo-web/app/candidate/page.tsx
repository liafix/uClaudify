import { PageHeader } from "../../components/candidate-shell";
import { roleMapping } from "../../data/candidate-evidence";

const nonClaims = [
  "No access to uCloudify client data, repositories or internal architecture.",
  "No claim of production banking tenure or commercial Python tenure.",
  "No claim that Terraform was applied to a real Azure subscription.",
  "No claim that formal education or language requirements are waived.",
] as const;

export default function CandidatePage() {
  return (
    <div className="demo-grid">
      <PageHeader
        eyebrow="CANDIDATE · ROLE-TO-EVIDENCE MAPPING"
        title="A focused answer to uCloudify’s technical signals"
        lede="This demo is intentionally narrow: Python-first finance data engineering with Java interoperability, Azure-compatible storage, Terraform infrastructure and read-only MCP operations."
      />
      <section className="panel role-grid">
        {roleMapping.map((item) => (
          <article key={item.signal} className="role-card">
            <div className="eyebrow">{item.signal}</div>
            <h2>{item.evidence}</h2>
            <p className="muted">{item.boundary}</p>
          </article>
        ))}
      </section>
      <section className="panel">
        <div className="eyebrow">EXPLICIT NON-CLAIMS</div>
        <h2>Candidate evidence, not inflated experience</h2>
        <div className="nonclaim-list">
          {nonClaims.map((item) => <p key={item}>— {item}</p>)}
        </div>
      </section>
    </div>
  );
}
