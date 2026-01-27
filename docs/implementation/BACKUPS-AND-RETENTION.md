# Backups and retention (T-132)

## Database

- **Automated backups:** Enable on Azure Database for PostgreSQL (Flexible Server) — backups are managed by Azure (point-in-time restore, retention per tier).
- **Retention:** Follow Azure PostgreSQL documentation; typically 7–35 days depending on SKU.
- **Restore procedure:**
  1. Azure Portal → your PostgreSQL server → Backups.
  2. Choose point-in-time restore; set target time and new server name.
  3. After restore, run migrations if any new ones exist; re-apply secrets (e.g. Key Vault `database-url`).
  4. Point apps to the restored DB connection string for validation; then cut over if replacing production.

## Blobs (exports, evidence)

- **Exports (audit packs):** Set lifecycle policy on the exports container to delete or tier objects older than 90 days (or per org policy).
- **Evidence packs:** Retention per workspace policy; lifecycle rules can expire older blobs in the evidence container.
- **Restore:** Blobs are not typically “restored” from backup for this workload; backups are enabled at the storage account level (e.g. soft delete, replication). Use Azure Storage restore features if a restore is required.
