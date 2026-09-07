export const candidateDisclaimer =
  "FinBridge Cloud is an independent synthetic candidate demonstration built for the uCloudify Junior Software Developer application. AlpineBank is fictional. No uCloudify client data, internal repositories, proprietary architecture, production credentials, or confidential processes are represented or used.";

export const goldenFacts = {
  batchId: "2026-09-05-001",
  input: 1024,
  accepted: 1019,
  duplicates: 3,
  invalidCurrency: 2,
  quarantined: 5,
  unaccounted: 0,
  accountability: "100%",
  opening: "€1,000,000.00",
  credits: "€125,400.00",
  debits: "€98,700.00",
  expectedClosing: "€1,026,700.00",
  calculatedClosing: "€1,026,700.00",
  difference: "€0.00",
  replay: "0 / 0 / 0",
  committedDatasets: 1,
  finalState: "READY_FOR_ANALYTICS",
} as const;

export const anomalies = [
  { id: "TX-00482", rule: "DQ-01", reason: "DUPLICATE_TRANSACTION" },
  { id: "TX-00791", rule: "DQ-01", reason: "DUPLICATE_TRANSACTION" },
  { id: "TX-00902", rule: "DQ-01", reason: "DUPLICATE_TRANSACTION" },
  { id: "TX-01011", rule: "DQ-02", reason: "INVALID_CURRENCY:EUX" },
  { id: "TX-01012", rule: "DQ-02", reason: "INVALID_CURRENCY:EURO" },
] as const;

export const mcpTools = [
  "get_batch_status",
  "get_data_quality_summary",
  "list_batch_anomalies",
  "trace_transaction",
  "get_reconciliation_result",
  "explain_quarantined_record",
] as const;

export const evidenceUsed = [
  "get_data_quality_summary",
  "list_batch_anomalies",
  "get_reconciliation_result",
] as const;

export const roleMapping = [
  {
    signal: "Predominantly Python",
    evidence: "DQ, finance, quarantine, reconciliation, idempotency and operations semantics",
    boundary: "Python owns validity and readiness decisions.",
  },
  {
    signal: "Java in mixed estates",
    evidence: "Executable LegacyTransaction model, canonical mapper and CSV export",
    boundary: "Java transports legacy data; it does not judge DQ or finance validity.",
  },
  {
    signal: "Azure / cloud migration",
    evidence: "Azure Blob-compatible storage, real Azurite validation and a thin Function boundary",
    boundary: "The candidate path stays local-first and cloud-independent.",
  },
  {
    signal: "Terraform / infrastructure",
    evidence: "Validated Resource Group, StorageV2, four private containers, Linux Y1 and Python 3.12 Function App",
    boundary: "No terraform apply or live-Azure claim.",
  },
  {
    signal: "MCP servers + AI agents",
    evidence: "Six read-only tools verified through the official MCP Python SDK v2 client",
    boundary: "AI explains deterministic evidence; it never mutates or decides validity.",
  },
  {
    signal: "Finance / data bridges",
    evidence: "Quality block, quarantine, exact reconciliation and idempotent replay",
    boundary: "Decimal finance invariants remain in Python.",
  },
] as const;
