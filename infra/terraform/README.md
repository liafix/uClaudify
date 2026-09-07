# FinBridge PASS 6 Terraform / Azure infrastructure contract

PASS 6 turns the PASS 0 Terraform placeholder into an executable Azure infrastructure contract while
keeping the candidate golden path local-first and credential-free.

Declared Azure resources:

- Resource Group
- StorageV2 account (Standard/LRS, TLS 1.2 minimum, private blob policy, blob versioning)
- private `raw`, `processed`, `quarantine`, and `audit` Blob containers
- Linux Consumption (`Y1`) Service Plan
- Linux Azure Function App running Python 3.12 / Functions `~4`

The Function App is wired to the same `FINBRIDGE_STORAGE` setting consumed by
`functions/azure/function_app.py`. Terraform provisions infrastructure only; deployment of Python
application code remains a separate release concern and is intentionally not hidden inside IaC.

## Validation (no Azure credentials required)

```bash
terraform -chdir=infra/terraform fmt -check -recursive
terraform -chdir=infra/terraform init -backend=false
terraform -chdir=infra/terraform validate
```

`terraform validate` checks provider-backed resource schemas after `init`; it does not create Azure
resources. **Do not run `terraform apply` as part of the candidate golden path.**

## Optional real Azure provisioning

For a future explicit cloud deployment, authenticate Azure separately, copy
`terraform.tfvars.example`, choose globally unique values for `storage_account_name` and
`function_app_name`, review `terraform plan`, and only then apply. PASS 6 itself does not claim that
an Azure subscription was provisioned.

## Local/Azurite independence

Nothing under `infra/terraform/` is imported by Python domain/storage/processing code. Local mode
continues to use `UseDevelopmentStorage=true` and `infra/azurite/docker-compose.yml`; the exact golden
path therefore remains usable without Terraform, Azure credentials, or an Azure subscription.
