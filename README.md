# FinBridge Cloud — PASS 8 Production-Hardening Review Candidate

This package starts from the reconstituted PASS 7 handoff. The original PASS 7 ZIP is unavailable, so no byte-for-byte identity claim is made for the reconstituted frontend. The handed-off ZIP was freshly baseline-revalidated before PASS 8 changes; that deterministic baseline was GREEN.

**PASS 8 review verdict in this execution environment: `BLOCKED_EXTERNAL_OR_TOOLCHAIN`, not GREEN.** Deterministic regression, Java, golden-path, contract, TypeScript fallback and repository secret/credential gates are green. Mandatory network/toolchain gates for Python ruff/mypy, clean Next.js production install/build, Terraform CLI runtime validation, official MCP Python SDK v2 runtime smoke and dependency vulnerability audits could not all execute here, so production-hardening closure is intentionally withheld.

No deploy step and no `terraform apply` are present. No live Azure resources, uCloudify internal data, production banking experience or browser/pixel-perfect QA are claimed. PASS 9 is not implemented.

Candidate routes: `/`, `/quality`, `/operations`, `/architecture`, `/candidate`.

# FinBridge Cloud

**Finance Data Modernization & AI Operations — uCloudify Candidate Demo**

FinBridge Cloud is an independent synthetic candidate demonstration built for the **uCloudify Junior
Software Developer** application. It demonstrates a reviewable modernization path from a fictional
legacy finance boundary to a Python-first, Azure-compatible data pipeline with explicit data
quality, financial reconciliation, persisted audit evidence and idempotency.

> **Synthetic-only disclaimer:** AlpineBank is fictional. No uCloudify client data, internal
> repositories, proprietary architecture, production credentials, or confidential processes are
> represented or used.

## Current status — PASS 8 review gate

PASS 0 froze the candidate/domain contract. PASS 1 implemented the executable recruitment vertical
slice. PASS 2 hardened DQ-01..DQ-05 and FIN-01..FIN-05. PASS 3 added persisted storage and real
Azurite evidence. PASS 4 added the real Java legacy adapter. PASS 5 added exactly six read-only MCP operations tools plus deterministic evidence-grounded
operations. **PASS 6 replaced the Terraform placeholder with an executable Azure infrastructure
contract for the Resource Group, StorageV2 evidence surfaces and Python Azure Function App, while
the local/Azurite golden path remains the default and requires no Azure credentials.** PASS 7 added
the five candidate routes and uCloudify role-to-evidence mapping. PASS 8 adds fail-closed CI/security/
production-hardening gates; in this runtime its review remains blocked only by unavailable external
network/toolchain prerequisites documented in `PASS8_REVIEW_GATE.md`.

Candidate path:

`LegacyTransaction (Java) -> Java mapper/export -> canonical CSV -> Python processing -> QUALITY BLOCKED -> quarantine -> reconciliation -> idempotent replay -> READY_FOR_ANALYTICS`

### PASS 4 Java boundary

Java owns only:

- fictional AlpineBank legacy transaction shape,
- deterministic synthetic legacy-source generation,
- `CR` / `DR` to canonical `CREDIT` / `DEBIT` transport mapping,
- canonical CSV export.

Java deliberately preserves the three duplicate transaction IDs and the invalid `EUX` / `EURO`
currencies. It does not decide whether those rows pass data quality.

Python remains the sole owner of DQ-01..DQ-05, FIN-01..FIN-05, quarantine, reconciliation,
idempotency and `READY_FOR_ANALYTICS`.

### Frozen executable evidence

- 1,024 synthetic input records
- 1,019 accepted records
- 3 duplicate records
- 2 invalid-currency records
- 5 quarantined records
- 0 unaccounted records after quarantine
- accepted credits: €125,400.00
- accepted debits: €98,700.00
- expected closing balance: €1,026,700.00
- calculated closing balance: €1,026,700.00
- reconciliation difference: €0.00
- exact replay: 0 new accepted / 0 duplicate imports / 0 additional quarantine
- persisted commit count after process restart: exactly 1

## Real integration evidence

PASS 3 storage was independently verified against real Azurite 3.37.0. PASS 4 was additionally
verified as a full **Java 21 -> Python -> azure-storage-blob 12.30.1 -> Azurite 3.37.0** flow.

The successful PASS 4 validation deployment emitted:

`PASS 4 real Java -> Python -> Azurite golden path: PASS`

See `PASS4_EVIDENCE.md` and `PASS4_REVIEW_GATE.md` for the exact validation identifiers and hashes.

## Repository map

```text
apps/demo-web/                  Candidate presentation of validated evidence
services/domain/                Python DQ + finance domain engine
services/storage/               Blob/Azurite/Azure persistence adapter
services/processing/            Storage orchestration + Java canonical CSV import boundary
services/mcp/                   PASS 5 read-only MCP tools + deterministic operations assistant
functions/azure/                Thin Azure Functions Blob-trigger boundary
adapters/legacy-java/           PASS 4 executable legacy model + mapper + CSV exporter
artifacts/pass4/                Verified Java-origin canonical batch + checksum
artifacts/pass5/                Controlled AI operations evidence + explicit evidence_used
infra/azurite/                  Local Azurite runtime definition
infra/terraform/                PASS 6 validated Azure Resource Group/Storage/Function IaC
fixtures/alpinebank/            Frozen synthetic scenario manifest
contracts/                      Frozen contract + current pass marker
docs/                           Architecture/pass decisions
scripts/                        Executable review gates + real-service smoke scripts
.github/workflows/              CI including Java -> Python -> Azurite PASS 4 smoke
```

## Run PASS 4 locally

```bash
./scripts/pass4_gate.sh
```

Generate a fresh canonical CSV from Java:

```bash
mkdir -p /tmp/finbridge-java
javac -d /tmp/finbridge-java $(find adapters/legacy-java/src/main/java -name '*.java' -type f | sort)
java -cp /tmp/finbridge-java com.finbridge.legacy.LegacyAdapterApp /tmp/java-canonical.csv
```

With Azurite and Azure SDK dependencies available:

```bash
PYTHONPATH=services/domain:services/storage:services/processing \
  python scripts/pass4_azurite_smoke.py /tmp/java-canonical.csv
```

## PASS 5 MCP operations boundary

PASS 5 exposes only `get_batch_status`, `get_data_quality_summary`, `list_batch_anomalies`,
`trace_transaction`, `get_reconciliation_result` and `explain_quarantined_record`. All are read-only.
The deterministic operations assistant includes `evidence_used` and has **no live LLM/API-key
dependency**. It cannot write storage, execute arbitrary SQL/shell commands or override Python DQ /
reconciliation decisions.
The primary MCP adapter uses the current official Python SDK v2 (`MCPServer`) and marks every tool
with explicit read-only/closed-world annotations.
The official SDK runtime gate is verified in a network-enabled environment with `mcp==2.1.1`: SHA-256-verified copies of this project’s `sdk_server.py` and six-tool smoke script executed through the official `Client(server)`, listing and calling all six tools with `readOnlyHint=true` and `openWorldHint=false`.

Runtime evidence: `PASS5_OFFICIAL_MCP_SDK_RUNTIME_EVIDENCE.md`.

Run the PASS 5 gate:

```bash
./scripts/pass5_gate.sh
```

## PASS 6 Terraform / Azure contract

PASS 6 declares the optional cloud-mode Resource Group, StorageV2 account, private `raw`,
`processed`, `quarantine`, and `audit` containers, Linux Consumption service plan, and Python 3.12
Azure Function App. The Function App is wired to the existing `FINBRIDGE_STORAGE` runtime contract.
Terraform is infrastructure-only: it does not own DQ/finance decisions and the candidate golden path
does not run `terraform apply`.

Validation:

```bash
./scripts/pass6_gate.sh
./scripts/pass6_terraform_gate.sh
```

See `docs/PASS6_TERRAFORM_AZURE_INFRASTRUCTURE.md`.

PASS 6 Terraform runtime validation is GREEN in a network-enabled environment: Terraform `1.16.1` + exact AzureRM `4.81.0` passed `fmt -check`, `init -backend=false`, and `validate` against the SHA-256-verified pinned source (`7ddfaea513e947fe1a4a3fed937aba94a1bb2d0048ab48af74afab04d7ce41e8`). See `PASS6_EVIDENCE.md` and `PASS6_REVIEW_GATE.md`. No `terraform apply` was executed and no live Azure subscription resources are claimed.

## PASS 8 production-hardening gate

The full gate is fail-closed:

```bash
./scripts/pass8_gate.sh
```

For a review run that executes every gate group and records PASS/BLOCKED/FAIL without stopping at the first blocked prerequisite:

```bash
./scripts/pass8_review_run.sh PASS8_FINAL_REGRESSION_2026-09-07.log
```

GitHub Actions definition: `.github/workflows/pass8-production-hardening.yml`. It contains seven independent jobs: Python, Java, frontend, Terraform, MCP, security and frozen golden-path regression. It performs no deployment and never executes `terraform apply`.

Not implemented in PASS 8: authentication, real financial data, real banking integrations, an actual Azure subscription deployment, or PASS 9. Browser/pixel-perfect QA was not executed in this runtime. See `PASS8_EVIDENCE.md` and `PASS8_REVIEW_GATE.md` for the exact executed-versus-blocked gate matrix.
