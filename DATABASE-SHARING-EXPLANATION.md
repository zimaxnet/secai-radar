# Database Server Sharing - Multi-Database Setup

## ✅ Yes, You Can Use the Same Server for Both Applications

PostgreSQL Flexible Servers support **multiple databases** on a single server instance. Each database is completely isolated from others.

## Current Setup

**Server:** `ctxeco-db` in `ctxeco-rg`

**Databases on Server:**
- `ctxeco` database (existing) - Used by ctxeco application
- `secairadar` database (new) - Used by secai-radar application
- `postgres` database (system default)

## How It Works

### Database Isolation
- Each database has its own:
  - Tables, indexes, views
  - Users and permissions (can be database-specific)
  - Data (completely separate)
- Applications connect to specific databases via connection string
- No data leakage between databases

### Resource Sharing
- **Shared Resources:**
  - CPU and memory (server-level)
  - Storage (server-level, but can monitor per-database)
  - Network bandwidth
  - Backup storage

- **Isolated:**
  - Data (database-level)
  - Schema (database-level)
  - Users/roles (can be database-specific)

## Connection Strings

### ctxeco Application
```
postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/ctxeco
```

### secai-radar Application
```
postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar
```

**Note:** Same server, same user, different database name.

## Benefits

1. **Cost Efficient** - No need for separate server
2. **Simplified Management** - One server to manage
3. **Resource Flexibility** - Can scale server if needed
4. **Isolation** - Complete data separation

## Considerations

### Performance
- Both applications share server resources
- Monitor server metrics (CPU, memory, connections)
- If one app is resource-intensive, it may impact the other
- **Solution:** Monitor and scale server if needed

### Backup & Recovery
- Backups are server-level (all databases)
- Can restore individual databases if needed
- Backup retention applies to all databases

### Security
- Same admin user (`ctxecoadmin`) for both
- Consider creating database-specific users for better isolation
- Firewall rules apply to entire server

### Scaling
- If you need to scale, you scale the entire server
- Both applications benefit from increased resources
- Can't scale databases independently

## Best Practices

### 1. Monitor Resource Usage
```bash
# Check server metrics in Azure Portal
# Monitor: CPU, Memory, Storage, Connections
```

### 2. Consider Database-Specific Users (Optional)
```sql
-- Create user for secai-radar (optional, for better isolation)
CREATE USER secairadar_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE secairadar TO secairadar_user;
```

### 3. Monitor Connection Limits
- PostgreSQL has connection limits
- Both apps share the connection pool
- Monitor active connections

### 4. Set Up Alerts
- Alert on high CPU/memory usage
- Alert on connection limit approaching
- Alert on storage usage

## When to Consider Separate Servers

Consider separate servers if:
- **High Resource Usage** - One app consumes most resources
- **Different Scaling Needs** - Apps need different performance tiers
- **Compliance Requirements** - Need physical/logical separation
- **Different Backup Policies** - Need different retention/backup schedules
- **Network Isolation** - Need different firewall rules per app

## Current Recommendation

✅ **Using shared server is fine for MVP/development**

For production, monitor:
- Server resource usage
- Application performance
- Connection counts
- Storage growth

If issues arise, you can:
1. Scale up the server (more CPU/memory)
2. Move one database to a separate server
3. Optimize queries to reduce resource usage

## Verification

Check existing databases:
```bash
az postgres flexible-server db list \
  --resource-group ctxeco-rg \
  --server-name ctxeco-db
```

Check server metrics:
- Azure Portal → PostgreSQL server → Metrics
- Monitor: CPU, Memory, Storage, Active Connections

## Summary

✅ **Yes, you can safely use the same server for both applications**

- Databases are isolated
- Same server, different databases
- Monitor resource usage
- Scale if needed

This is a common and recommended approach for development and MVP stages.
