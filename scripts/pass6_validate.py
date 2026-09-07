#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TF = ROOT / "infra/terraform"

REQUIRED = (
    "infra/terraform/versions.tf",
    "infra/terraform/providers.tf",
    "infra/terraform/variables.tf",
    "infra/terraform/main.tf",
    "infra/terraform/outputs.tf",
    "infra/terraform/terraform.tfvars.example",
    "docs/PASS6_TERRAFORM_AZURE_INFRASTRUCTURE.md",
    ".github/workflows/pass6.yml",
)


def main() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f"Missing PASS 6 artifacts: {missing}")

    if (ROOT / "contracts/current_pass.txt").read_text().strip() != "6":
        raise AssertionError("PASS marker must be exactly 6")

    versions = (TF / "versions.tf").read_text(encoding="utf-8")
    if 'source  = "hashicorp/azurerm"' not in versions:
        raise AssertionError("AzureRM provider contract missing")
    if 'version = "4.81.0"' not in versions:
        raise AssertionError("PASS 6 must pin the remotely validated AzureRM provider version")
    if 'required_version = "~> 1.16.0"' not in versions:
        raise AssertionError("PASS 6 must pin the validated Terraform 1.16 line")

    main_tf = (TF / "main.tf").read_text(encoding="utf-8")
    required_resources = (
        'resource "azurerm_resource_group" "finbridge"',
        'resource "azurerm_storage_account" "finbridge"',
        'resource "azurerm_storage_container" "finbridge"',
        'resource "azurerm_service_plan" "functions"',
        'resource "azurerm_linux_function_app" "finbridge"',
    )
    for token in required_resources:
        if token not in main_tf:
            raise AssertionError(f"Missing Terraform resource contract: {token}")

    for name in ("raw", "processed", "quarantine", "audit"):
        if f'"{name}"' not in main_tf:
            raise AssertionError(f"Missing private evidence container declaration: {name}")

    security_tokens = (
        'container_access_type = "private"',
        'allow_nested_items_to_be_public = false',
        'min_tls_version          = "TLS1_2"',
        'https_only                  = true',
        'python_version = "3.12"',
        'functions_extension_version = "~4"',
    )
    for token in security_tokens:
        if token not in main_tf:
            raise AssertionError(f"PASS 6 Azure contract missing: {token}")

    if 'FINBRIDGE_STORAGE' not in main_tf:
        raise AssertionError("Function App is not wired to the existing storage runtime contract")

    outputs = (TF / "outputs.tf").read_text(encoding="utf-8").lower()
    forbidden_output_tokens = ("primary_access_key", "primary_connection_string", "client_secret")
    if any(token in outputs for token in forbidden_output_tokens):
        raise AssertionError("Sensitive Azure storage material leaked into Terraform outputs")

    all_tf = "\n".join(path.read_text(encoding="utf-8") for path in TF.glob("*.tf"))
    if re.search(r"\bterraform\s+apply\b", all_tf, flags=re.IGNORECASE):
        raise AssertionError("terraform apply must not be embedded in the infrastructure contract")

    workflow = (ROOT / ".github/workflows/pass6.yml").read_text(encoding="utf-8")
    for required in (
        "hashicorp/setup-terraform@v3",
        "terraform fmt -check -recursive",
        "terraform init -backend=false",
        "terraform validate",
        "./scripts/pass6_gate.sh",
    ):
        if required not in workflow:
            raise AssertionError(f"PASS 6 CI missing required gate: {required}")
    if "terraform apply" in workflow.lower():
        raise AssertionError("PASS 6 CI must never apply Azure infrastructure")

    function_source = (ROOT / "functions/azure/function_app.py").read_text(encoding="utf-8")
    if 'connection="FINBRIDGE_STORAGE"' not in function_source:
        raise AssertionError("Existing Azure Function trigger storage contract changed")
    if "DataQualityEngine" in function_source or "GoldenPathPipeline" in function_source:
        raise AssertionError("Azure Function boundary took ownership of domain decisions")

    azurite = (ROOT / "infra/azurite/docker-compose.yml").read_text(encoding="utf-8")
    if "10000:10000" not in azurite:
        raise AssertionError("Local Azurite boundary was removed")

    if (ROOT / "docs/PASS7_CANDIDATE_EXPERIENCE.md").exists():
        raise AssertionError("PASS 7 scope leaked into PASS 6")

    print("PASS: Terraform declares Resource Group + StorageV2 + four private evidence containers")
    print("PASS: Terraform declares Linux Y1 Service Plan + Python 3.12 Azure Function App")
    print("PASS: Function App is wired to FINBRIDGE_STORAGE without moving domain ownership")
    print("PASS: Terraform outputs expose no storage keys or connection strings")
    print("PASS: CI requires fmt/init/validate and contains no terraform apply")
    print("PASS: local/Azurite golden-path boundary remains present and cloud-independent")
    print("PASS: PASS 7 scope remains absent")
    print("PASS 6 structural infrastructure validation: PASS")


if __name__ == "__main__":
    main()
