// SecAI Radar Verified MCP Infrastructure
// Based on Step 5: Reference Implementation Plan
// Azure Container Apps, PostgreSQL, Storage, Key Vault

targetScope = 'resourceGroup'

@description('Name of the resource group (passed from subscription-level deployment)')
param resourceGroupName string

@description('Azure region for all resources')
param location string = 'centralus'

@description('Environment suffix (dev, preprod, prod)')
param environment string = 'dev'

@description('Base application name')
param appName string = 'secai-radar'

// ============================================================================
// PostgreSQL Database
// ============================================================================

resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: '${appName}-${environment}-postgres'
  location: location
  sku: {
    name: 'Standard_B1ms' // MVP: Basic tier, upgrade for production
    tier: 'Burstable'
  }
  properties: {
    version: '15'
    administratorLogin: 'secairadar'
    administratorLoginPassword: '@secureString()' // Should use Key Vault reference
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    maintenanceWindow: {
      customWindow: 'Enabled'
      dayOfWeek: 0
      startHour: 2
      startMinute: 0
    }
  }
}

resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-06-01-preview' = {
  parent: postgresServer
  name: 'secairadar'
}

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
// Container Apps (Public API)
// ============================================================================

resource publicApiApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appName}-${environment}-public-api'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: false
        transport: 'http'
      }
      secrets: [
        {
          name: 'database-connection'
          value: 'postgresql://...' // Should reference Key Vault
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: '${appName}/public-api:latest'
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'database-connection'
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
      }
    }
  }
}

// ============================================================================
// Container Apps (Registry API - Private)
// ============================================================================

resource registryApiApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appName}-${environment}-registry-api'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: false
        transport: 'http'
      }
      secrets: [
        {
          name: 'database-connection'
          value: 'postgresql://...' // Should reference Key Vault
        }
        {
          name: 'entra-tenant-id'
          value: '@secureString()' // Should reference Key Vault
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: '${appName}/registry-api:latest'
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'database-connection'
            }
            {
              name: 'ENTRA_TENANT_ID'
              secretRef: 'entra-tenant-id'
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
      }
    }
  }
}

// ============================================================================
// Container Apps Jobs (Pipeline Workers)
// ============================================================================

resource pipelineWorkersEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${appName}-${environment}-workers-env'
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

// Example: Scout Worker Job
resource scoutJob 'Microsoft.App/jobs@2023-05-01' = {
  name: '${appName}-${environment}-scout'
  location: location
  properties: {
    environmentId: pipelineWorkersEnv.id
    configuration: {
      triggerType: 'Schedule'
      scheduleTriggerConfig: {
        cronExpression: '30 2 * * *' // 02:30 daily (America/Phoenix)
        parallelism: 1
        replicaCompletionCount: 1
      }
      secrets: [
        {
          name: 'database-connection'
          value: 'postgresql://...'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'scout'
          image: '${appName}/scout:latest'
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'database-connection'
            }
            {
              name: 'ENVIRONMENT'
              value: environment
            }
          ]
        }
      ]
    }
  }
}

// Similar jobs for: Curator, EvidenceMiner, Scorer, DriftSentinel, Publisher, SageMeridian

// ============================================================================
// Outputs
// ============================================================================

output postgresServerName string = postgresServer.name
output postgresServerFqdn string = postgresServer.properties.fullyQualifiedDomainName
output storageAccountName string = storageAccount.name
output keyVaultName string = keyVault.name
output publicApiUrl string = 'https://${publicApiApp.properties.configuration.ingress.fqdn}'
output registryApiUrl string = 'https://${registryApiApp.properties.configuration.ingress.fqdn}'
