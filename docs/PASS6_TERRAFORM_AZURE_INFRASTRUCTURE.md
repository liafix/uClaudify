# PASS 6 — Terraform + Azure infrastructure contract

## Goal

Describe the optional Azure deployment as executable IaC without turning cloud availability into a
dependency of the FinBridge candidate demo.

## Resource contract

Terraform now declares:

1. `azurerm_resource_group.finbridge`
2. `azurerm_storage_account.finbridge`
3. four private `azurerm_storage_container.finbridge` instances: `raw`, `processed`, `quarantine`, `audit`
4. Linux `azurerm_service_plan.functions` using Consumption SKU `Y1`
5. `azurerm_linux_function_app.finbridge` using Python 3.12 / Functions `~4`

The Function App receives `FINBRIDGE_STORAGE` plus explicit container-name settings and therefore
matches the storage vocabulary already proven in PASS 3. The Function App remains a trigger/wiring
boundary: Python still owns DQ-01..DQ-05, FIN-01..FIN-05, quarantine, reconciliation and readiness.

## Security/review posture

- storage containers are private;
- nested public blob access is disabled;
- TLS 1.2 is the minimum storage transport version;
- HTTPS is required on the Function App;
- no storage key/connection-string output is exported;
- no credentials are committed;
- no `terraform apply` is part of any regression or candidate-demo gate.

The Function App currently receives its storage connection string through an Azure app setting so it
matches the existing `FINBRIDGE_STORAGE` runtime contract. This value is sensitive cloud state and is
never emitted as a Terraform output. A managed-identity conversion is a possible future hardening,
not required to prove PASS 6 infrastructure reproducibility.

## Validation boundary

PASS 6 acceptance requires real Terraform CLI/provider-schema validation:

```text
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

No Azure credentials are required for these checks, and a green validate must not be represented as
an Azure deployment.

## Local-first invariant

`infra/azurite/docker-compose.yml`, `UseDevelopmentStorage=true`, the Python storage adapters and the
golden path remain unchanged. Terraform does not appear in domain/processing runtime imports. The
candidate can therefore demonstrate the full finance evidence path offline even if Azure is
unavailable.

## Explicit non-goals

PASS 6 does not:

- execute `terraform apply`;
- claim ownership of a live Azure subscription;
- deploy the Function App source package;
- add queues/Kafka/Kubernetes/Databricks;
- alter PASS 5 MCP behavior;
- start PASS 7 candidate UX/presentation work.
