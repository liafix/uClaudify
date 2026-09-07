# PASS 0 Evidence

## Local validation executed

`./scripts/pass0_gate.sh`

Observed result:

- structural/domain validator: PASS
- frozen scenario: PASS
- candidate scope contract: PASS
- secret hygiene: PASS
- later-pass isolation: PASS
- Python frozen-contract tests: **6/6 PASS**
- Java legacy-boundary compile/contract smoke: PASS
- TypeScript candidate-shell typecheck: PASS
- candidate-shell content contract: PASS
- aggregate PASS 0 gate: **GREEN**

## Toolchain used in the validation environment

- Node.js 22.16.0
- npm 10.9.2
- Python 3.13.5 executing a Python >=3.12-compatible contract
- OpenJDK 21.0.11
- Git 2.47.3

## Terraform evidence status

The local execution environment does not contain the Terraform CLI, so `terraform init/validate` was not falsely claimed as locally executed. The repository includes a dedicated GitHub Actions job using `hashicorp/setup-terraform` to run:

- `terraform fmt -check`
- `terraform init -backend=false`
- `terraform validate`

Actual Azure resources are intentionally deferred to PASS 6; PASS 0 freezes only provider/version/naming foundations.

## Scope integrity

PASS 0 does **not** implement ingestion, quarantine, reconciliation, replay, Azure Function runtime, MCP, live AI, authentication or deployment. Those remain gated behind explicit approval of subsequent passes.
