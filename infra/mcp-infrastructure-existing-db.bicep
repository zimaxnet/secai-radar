// SecAI Radar Verified MCP Infrastructure
// Using existing PostgreSQL server in ctxeco-rg
// Based on Step 5: Reference Implementation Plan

targetScope = 'resourceGroup'

@description('Name of the resource group (passed from subscription-level deployment)')
param resourceGroupName string

@description('Azure region for all resources')
param location string = 'centralus'

@description('Environment suffix (dev, preprod, prod)')
param environment string = 'dev'

@description('Base application name')
param appName string = 'secai-radar'

@description('Existing PostgreSQL server resource group')
param existingPostgresResourceGroup string = 'ctxeco-rg'

@description('Existing PostgreSQL server name')
param existingPostgresServerName string = 'ctxeco-db'

// ============================================================================
// PostgreSQL Database (Using Existing Server)
// ============================================================================
// Note: We reference the existing PostgreSQL server but don't create it
// The database will be created via migration scripts

// Reference to existing PostgreSQL server (for outputs and firewall rules)
var existingPostgresServerId = resourceId(existingPostgresResourceGroup, 'Microsoft.DBforPostgreSQL/flexibleServers', existingPostgresServerName)

// ============================================================================
// Storage Account (Evidence + Assets)
// ============================================================================

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-04-01' = {
  name: '${toLower(appName)}${environment}sa'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
  }
}

resource evidenceContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-04-01' = {
  parent: storageAccount::blobServices
  name: 'evidence-private'
  properties: {
    publicAccess: 'None'
  }
}

resource publicAssetsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-04-01' = {
  parent: storageAccount::blobServices
  name: 'public-assets'
  properties: {
    publicAccess: 'Blob'
  }
}

resource exportsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-04-01' = {
  parent: storageAccount::blobServices
  name: 'exports-private'
  properties: {
    publicAccess: 'None'
  }
}

// ============================================================================
// Key Vault
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${appName}-${environment}-kv'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: false
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    accessPolicies: []
    publicNetworkAccess: 'Enabled'
  }
}

// ============================================================================
// Log Analytics Workspace
// ============================================================================

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${appName}-${environment}-law'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ============================================================================
// Container Apps Environment
// ============================================================================

resource containerAppsEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${appName}-${environment}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
      }
    }
  }
}

// ============================================================================
// Container Registry (ACR)
// ============================================================================

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: '${toLower(appName)}${environment}acr'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// ============================================================================
// Outputs
// ============================================================================

output storageAccountName string = storageAccount.name
output storageAccountKey string = storageAccount.listKeys().keys[0].value
output keyVaultName string = keyVault.name
output containerAppsEnvName string = containerAppsEnv.name
output containerRegistryName string = containerRegistry.name
output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
output existingPostgresServerId string = existingPostgresServerId
output existingPostgresServerName string = existingPostgresServerName
output existingPostgresResourceGroup string = existingPostgresResourceGroup
