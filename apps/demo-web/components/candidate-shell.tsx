import type { ReactNode } from "react";
import { candidateDisclaimer } from "../data/candidate-evidence";

const nav = [
  ["/", "Pipeline"],
  ["/quality", "Quality"],
  ["/operations", "AI Operations"],
  ["/architecture", "Architecture"],
  ["/candidate", "Candidate"],
] as const;

export function CandidateShell({ children }: { children: ReactNode }) {
  return (
    <main className="shell">
      <header className="topbar panel">
        <div>
          <div className="eyebrow">FINBRIDGE CLOUD · UCLOUDIFY CANDIDATE DEMO</div>
          <strong className="brand">Finance data modernization workbench</strong>
        </div>
        <nav className="nav" aria-label="Candidate demo navigation">
          {nav.map(([href, label]) => (
            <a key={href} href={href}>{label}</a>
          ))}
        </nav>
      </header>
      {children}
      <section className="panel disclaimer footer-disclaimer">
        <strong>Independent synthetic candidate demonstration.</strong>
        <p>{candidateDisclaimer}</p>
      </section>
    </main>
  );
}

export function PageHeader({ eyebrow, title, lede }: { eyebrow: string; title: string; lede: string }) {
  return (
    <section className="panel hero-panel page-hero">
      <div className="eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
      <p className="lede">{lede}</p>
    </section>
  );
}
