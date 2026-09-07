# PASS 8 CI Continuity Fix — 2026-09-07

## Finding

Static review of `.github/workflows/pass8-production-hardening.yml` found that the frontend job configured `actions/setup-node@v4` npm caching with `cache-dependency-path: apps/demo-web/package.json` while the repository intentionally has no committed npm lockfile.

`setup-node` cache dependency paths are intended for supported dependency/lock files. For a workflow that creates the lockfile inside the job, pre-install cache configuration cannot safely key from `package.json` as though it were the lockfile.

## Fix

Removed the `cache: npm` and `cache-dependency-path` inputs from the frontend `setup-node` step. The frontend gate still performs the required clean path:

1. delete `node_modules`, `.next`, and any generated `package-lock.json`;
2. generate a fresh lockfile with `npm install --package-lock-only`;
3. execute `npm ci`;
4. run frontend contract, TypeScript typecheck and optimized production build;
5. verify all five built routes plus noindex and synthetic disclaimer.

The security job already performs its own clean dependency materialization and was left fail-closed.

## Boundary

This is a CI continuity fix only. It changes no Python/Java/domain/frontend candidate semantics, no Terraform definitions and no MCP behavior.

Post-fix local evidence is recorded in `PASS8_POST_FIX_AUTHORITATIVE_LOCAL_REGRESSION_2026-09-07.log`.
