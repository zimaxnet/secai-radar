# Archived Documentation

This folder contains archived documentation that is **not essential** for the MVP implementation. These documents are preserved for historical reference but are not part of the current architecture based on `blueprint.md`.

## Archive Structure

### `legacy-deployment/`
Legacy deployment and configuration documentation for the old Azure Functions/SWA architecture. These documents are specific to the previous implementation and may not align with the new blueprint architecture.

Includes:
- Azure Functions deployment guides
- Authentication setup (Entra ID)
- Azure portal configuration
- Troubleshooting and fix guides
- Migration guides

### `status-docs/`
Status documents, setup checklists, and completion guides from previous implementation phases. These are historical status updates that are no longer relevant.

Includes:
- Status summaries and checklists
- Setup completion guides
- Previous build briefs
- Change summaries

### `adr-archive/`
Archived Architecture Decision Records (ADRs) from the previous architecture. These decisions were made for the old Azure-native architecture and may not apply to the new blueprint-based architecture.

Includes:
- ADR 0001-0005 (previous architecture decisions)
- Decision log index

### `backlog.md`
Previous feature backlog. New features should be planned based on `blueprint.md` objectives.

## When to Reference Archived Docs

- **Historical context**: Understanding previous implementation decisions
- **Migration planning**: If migrating from old architecture
- **Troubleshooting**: Reference to old deployment issues
- **Decision tracking**: Understanding previous architectural choices

## Note

For current development, **always reference `blueprint.md`** as the authoritative source for architecture and implementation guidance.

