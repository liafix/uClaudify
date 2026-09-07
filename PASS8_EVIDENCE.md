# FinBridge Cloud — PASS 8 Evidence

**Pass:** 8 — CI + Production Hardening  
**Execution date:** 2026-09-07  
**Stop condition:** PASS 8 review gate only; PASS 9 is not implemented.  
**Verdict:** **BLOCKED_EXTERNAL_OR_TOOLCHAIN — not GREEN**

## 1. Provenance and baseline re-validation

Input archive:

`FinBridge_Cloud_uCloudify_Candidate_Demo_PASS7_RECONSTITUTED_HANDOFF(1).zip`

Input SHA-256:

`94c8d1bbbf409913b38610d0d561c478b2229a9987f5d0502c3b9255e8e5050f`

The archive explicitly states that PASS 7 was reconstituted from the final PASS 6 codebase plus preserved PASS 7 evidence and reimplemented candidate-experience source. The original PASS 7 frontend archive is unavailable; this package therefore does **not** claim byte-for-byte identity with that original archive.

Before PASS 8 changes, the exact handed-off ZIP passed its reconstituted PASS 7 gate:

- 27/27 domain tests
- 3/3 storage tests
- 6/6 processing tests
- 16/16 MCP tests
- Java -> Python -> storage smoke: PASS
- MCP stdio JSON-RPC smoke: PASS
- compileall: PASS
- PASS 7 structural candidate experience: PASS

Baseline log: `PASS8_BASELINE_REVALIDATION_2026-09-07.log`.

## 2. Frozen golden path

PASS 8 did not change the frozen finance/data result:

- batch `2026-09-05-001`
- input: 1,024
- accepted: 1,019
- DQ-01 duplicates: 3
- DQ-02 invalid currencies: 2
- quarantined: 5
- unaccounted: 0
- record accountability: 100%
- opening: €1,000,000.00
- credits: €125,400.00
- debits: €98,700.00
- expected closing: €1,026,700.00
- calculated closing: €1,026,700.00
- difference: €0.00
- replay: 0 new accepted / 0 duplicate imports / 0 additional quarantine
- committed dataset count: exactly 1
- final state: `READY_FOR_ANALYTICS`

`python3 scripts/pass8_golden_regression.py` is GREEN.

## 3. Prior-pass contract regression

PASS 0 through PASS 5 later-pass-compatible structural/ownership validators are GREEN. In particular:

- Python remains the sole owner of DQ-01..DQ-05, FIN-01..FIN-05, quarantine, reconciliation, idempotency and readiness.
- Java remains mapping/export only and preserves invalid/duplicate data for Python to judge.
- MCP remains exactly six read-only operations tools, with no arbitrary SQL, shell or mutation surface.
- AI operations evidence remains deterministic and requires no live LLM fallback.

Log: `PASS8_PRIOR_PASS_CONTRACT_REGRESSION_2026-09-07.log`.

PASS 6's historical validator is intentionally scope-stopped at current-pass marker `6`, so it is not reused as a PASS 8 result. Instead PASS 8 verifies all six Terraform source files against the exact SHA-256 values recorded by PASS 6. All six match the previously validated source byte-for-byte. This continuity check is **not** substituted for a fresh Terraform runtime gate.

## 4. Python

Executed locally:

- unit/regression suite: **52/52 PASS** total (`27 + 3 + 6 + 16`)
- `python3 -m compileall`: PASS

Required full PASS 8 static gate:

- `ruff`: **BLOCKED_TOOLCHAIN** in this runtime
- `mypy`: not executed because the fail-closed static gate stops on missing required tooling
- direct Python runtime dependencies are pinned for PASS 8 in `requirements-pass8.txt` / `pyproject.toml`:
  - `azure-functions==1.25.0`
  - `azure-storage-blob==12.30.1`
  - `mcp==2.1.1`

The GitHub Actions Python job installs `ruff` and `mypy` and runs the full gate. This workflow was created but was not executed on GitHub in this runtime.

## 5. Java

Executed locally with Java 21:

- compile: PASS
- PASS 0 canonical contract test: PASS
- PASS 4 mapping/export test: PASS
- canonical export: 1,024 rows: PASS
- Java -> Python -> in-memory storage regression: PASS

Java ownership remains structural mapping/export only; it does not own finance or DQ decisions.

## 6. Frontend

Candidate routes remain:

- `/`
- `/quality`
- `/operations`
- `/architecture`
- `/candidate`

Executed locally:

- PASS 7 frontend source contract: PASS
- global TypeScript 5.8.3 fallback typecheck: PASS
- source noindex/nofollow metadata: PASS
- synthetic disclaimer and explicit non-claims: PASS

Mandatory clean production gate:

- clean dependency resolution/install: **BLOCKED_NETWORK** (`registry.npmjs.org` unreachable from this runtime)
- package-lock generation + `npm ci`: BLOCKED_NETWORK
- normal project TypeScript typecheck after clean install: BLOCKED_NETWORK
- optimized Next.js production build: BLOCKED_NETWORK
- built-output verification for all five routes: BLOCKED_NETWORK
- built-output noindex/disclaimer verification: BLOCKED_NETWORK

No browser or pixel-perfect QA claim is made.

## 7. Terraform

Preserved pins:

- Terraform required version: `~> 1.16.0`
- AzureRM: exact `4.81.0`

All six Terraform source hashes still match the exact PASS 6 externally validated source. However, this runtime does not provide the Terraform CLI and network retrieval was unavailable. Therefore:

- `terraform fmt -check -recursive`: **BLOCKED_TOOLCHAIN**
- `terraform init -backend=false`: **BLOCKED_TOOLCHAIN**
- `terraform validate`: **BLOCKED_TOOLCHAIN**

No `terraform apply` was executed. No live Azure resource is claimed.

## 8. MCP

Executed locally:

- MCP suite: **16/16 PASS** (included in the 52-test Python total)
- stdio JSON-RPC initialize / tools/list / tools/call smoke: PASS
- exactly six tool names: structurally PASS
- `readOnlyHint=true`: structurally PASS
- `openWorldHint=false`: structurally PASS
- arbitrary SQL/shell/mutation tools: absent
- live LLM fallback: absent

The current `sdk_server.py` and official SDK smoke script remain byte-identical to the files previously hash-verified and executed with `mcp==2.1.1` in PASS 5. A fresh PASS 8 official SDK runtime smoke is still **BLOCKED_TOOLCHAIN** because `mcp` is not installed and package retrieval is unavailable here. Historical PASS 5 execution is not relabeled as a PASS 8 runtime PASS.

## 9. Security

Repository fail-closed secret/credential scanner: PASS.

It rejects credential/state files and scans source/artifacts for private keys, API-key/token patterns, Azure storage connection strings and assignment-shaped secrets. Final scan result: **191 files inspected, PASS**. The same result is captured in `PASS8_FINAL_REGRESSION_2026-09-07.log`.

Dependency vulnerability gates:

- `pip-audit`: **BLOCKED_TOOLCHAIN / network-dependent resolution unavailable**
- `npm audit --audit-level=low`: **BLOCKED_NETWORK** because the clean install cannot be completed
- exact vulnerability severity counts: **NOT AVAILABLE; no PASS claim made**

This is a closure blocker. PASS 8 does not claim zero vulnerabilities.

## 10. CI implementation

Created `.github/workflows/pass8-production-hardening.yml` with seven independent fail-closed jobs:

1. Python
2. Java
3. frontend
4. Terraform
5. MCP
6. security
7. golden-path regression

The workflow has read-only repository permissions, no deploy job/step, and no `terraform apply`. YAML parsing of the workflow passed locally.

## 11. PASS 8 review-run result

The review runner executes every gate group even when some prerequisites are unavailable, while returning non-zero unless every group is GREEN.

Authoritative log: `PASS8_FINAL_REGRESSION_2026-09-07.log`.

Final review groups: **11 total = 6 PASS / 5 BLOCKED / 0 FAIL**. The closure verdict is `BLOCKED_EXTERNAL_OR_TOOLCHAIN`.

## 12. Claim discipline

This package does not claim:

- live Azure deployment or provisioned Azure resources
- uCloudify internal data, architecture, repositories or confidential processes
- production banking experience
- commercial Python tenure
- browser/pixel-perfect QA
- fulfillment or waiver of education/language requirements
- a clean dependency-vulnerability audit when the scanner could not run

PASS 9 is not implemented.

## 13. Post-review CI continuity correction — 2026-09-07

A static review after the original PASS 8 review gate found one CI continuity defect in the frontend GitHub Actions job: `actions/setup-node@v4` was configured to use npm caching with `apps/demo-web/package.json` as `cache-dependency-path` even though this package intentionally does not commit a lockfile. The cache inputs were removed; the job still creates a fresh lockfile, performs `npm ci`, typechecks, builds and verifies the built routes/disclaimers when network access is available.

This was a CI-only continuity correction. It changed no domain logic, frontend candidate semantics, Terraform definitions or MCP behavior. Post-fix local regression is GREEN and the frozen golden path remains exact. See `PASS8_CI_CONTINUITY_FIX_2026-09-07.md` and `PASS8_POST_FIX_AUTHORITATIVE_LOCAL_REGRESSION_2026-09-07.log`.

The correction does **not** unblock the five mandatory external/toolchain groups. PASS 8 therefore remains `BLOCKED_EXTERNAL_OR_TOOLCHAIN`, not GREEN.

Post-continuity artifact scan after adding the scope-recovery/precheck documentation: **198 files inspected, PASS**. No secret/credential finding was introduced.
