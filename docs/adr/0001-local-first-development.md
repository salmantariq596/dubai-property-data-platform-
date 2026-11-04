# ADR 0001: Develop locally and on Databricks Free Edition before Azure

- **Status:** Accepted
- **Date:** 2026-11-04

## Context

The Azure free account gives a credit that expires 30 days after activation, and the Azure Databricks trial lasts 14 days. Building and debugging pipeline logic takes several weeks. Spending those weeks on paid cloud time would burn the credits before the platform is ready to deploy.

## Decision

- All transformation logic lives in the `src/dubai_property` Python package and is unit-tested locally with pytest.
- Notebook development (Modules 2–5) runs on Databricks Free Edition.
- The Azure account is activated only in Module 7, once the local pipeline passes all tests.
- Only one year of data is used until the pipeline works end to end; full history is backfilled afterwards.

## Consequences

- Cloud credits are spent on deployment and the full-history run, not on debugging.
- Code must not depend on Free Edition specifics (for example, paths are passed as parameters), so it runs unchanged on Azure Databricks.
- Some Azure-only features (ADF, managed identity, Key Vault) are not exercised until Module 7, so integration risk is concentrated there.
