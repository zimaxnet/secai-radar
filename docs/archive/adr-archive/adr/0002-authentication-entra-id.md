# ADR 0002: Authentication via Entra ID (Azure AD)

- **Status:** Accepted
- **Date:** 2025-11-03

## Context
Consultants will access customer-specific data; we need SSO with Azure tenants and role-based access.

## Decision
Use **Entra ID** integration via **Azure Static Web Apps** for SPA auth and route protection. Functions receive user info via headers (EasyAuth).

## Options Considered
- SWA Entra auth (Chosen): simplest, integrated with hosting.
- MSAL-only SPA + custom Function auth: more flexibility, more work.
- No auth initially: not acceptable for real assessments.

## Consequences
- + Rapid setup, minimal code for auth.
- + Easy per-route protection and roles.
- - Tighter coupling to SWA hosting model.
- Follow-ups: define roles (consultant, viewer), tenant scoping mechanism.

## References
- SWA auth docs
