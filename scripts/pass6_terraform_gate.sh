#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v terraform >/dev/null 2>&1; then
  echo "ERROR: Terraform CLI is required for PASS 6 fmt/init/validate" >&2
  exit 2
fi

terraform version
terraform -chdir="$ROOT/infra/terraform" fmt -check -recursive
terraform -chdir="$ROOT/infra/terraform" init -backend=false -input=false
terraform -chdir="$ROOT/infra/terraform" validate

echo "PASS 6 TERRAFORM GATE: GREEN"
