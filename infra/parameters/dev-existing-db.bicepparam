using '../mcp-infrastructure-existing-db.bicep'

param resourceGroupName = 'secai-radar-rg'
param location = 'centralus'
param environment = 'dev'
param appName = 'secai-radar'
param existingPostgresResourceGroup = 'ctxeco-rg'
param existingPostgresServerName = 'ctxeco-db'
