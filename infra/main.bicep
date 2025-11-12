targetScope = 'subscription'

@description('Name of the resource group to deploy SecAI Radar resources into.')
param resourceGroupName string

@description('Azure region for all resources.')
param location string = 'eastus2'

@description('Environment suffix (dev, preprod, prod). Used in resource naming and tags.')
param environment string = 'dev'

@description('Base application name used for naming resources.')
param appName string = 'secai-radar'

@description('Docker image (including tag) for the Function App container.')
param functionContainerImage string = 'zimaxnet/secai-radar-api:latest'

@description('Azure Functions plan SKU name (EP1, EP2, EP3).')
@allowed([
  'EP1'
  'EP2'
  'EP3'
])
param functionPlanSkuName string = 'EP1'

@description('Number of pre-warmed instances to keep online. Set to 0 for cost savings.')
@minValue(0)
@maxValue(20)
param preWarmedInstanceCount int = 0

@description('Maximum elastic workers available for burst scaling.')
@minValue(1)
@maxValue(20)
param maximumElasticWorkerCount int = 10

@description('Storage account name (must be globally unique, lowercase, 3-24 chars).')
param storageAccountName string = toLower('${appName}${environment}sa')

@description('Application Insights daily cap in GB (0 disables).')
@minValue(0)
@maxValue(100)
param appInsightsDailyCapGb int = 1

@description('Application Insights sampling percentage (0-100).')
@minValue(0)
@maxValue(100)
param appInsightsSamplingPercentage int = 5

var functionPlanName = '${appName}-${environment}-plan'
var functionAppName = '${appName}-${environment}-api'
var aiQueueName = 'ai-jobs'

resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: resourceGroupName
  location: location
  tags: {
    environment: environment
    application: appName
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-04-01' = {
  name: storageAccountName
  scope: rg
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
  }
  tags: {
    environment: environment
    application: appName
  }
}

resource queueService 'Microsoft.Storage/storageAccounts/queueServices@2023-01-01' = {
  parent: storage
  name: 'default'
}

resource aiQueue 'Microsoft.Storage/storageAccounts/queueServices/queues@2023-01-01' = {
  parent: queueService
  name: aiQueueName
}

resource functionPlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: functionPlanName
  scope: rg
  location: location
  kind: 'functionapp'
  sku: {
    name: functionPlanSkuName
    tier: 'ElasticPremium'
    size: functionPlanSkuName
  }
  properties: {
    maximumElasticWorkerCount: maximumElasticWorkerCount
    reserved: true
    targetWorkerCount: 0
    targetWorkerSizeId: 0
    perSiteScaling: false
    preWarmedInstanceCount: preWarmedInstanceCount
  }
  tags: {
    environment: environment
    application: appName
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${appName}-${environment}-appi'
  scope: rg
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Redfield'
    Request_Source: 'rest'
    SamplingPercentage: appInsightsSamplingPercentage
    DailyQuota: appInsightsDailyCapGb
  }
  tags: {
    environment: environment
    application: appName
  }
}

resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: functionAppName
  scope: rg
  location: location
  kind: 'functionapp,linux,container'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: functionPlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'DOCKER|${functionContainerImage}'
      appSettings: [
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'AzureWebJobsStorage'
          value: storage.listKeys().keys[0].connectionString
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: storage.listKeys().keys[0].connectionString
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(replace('${functionAppName}${environment}', '-', ''))
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '0'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'QUEUE_NAME_AI_JOBS'
          value: aiQueueName
        }
        {
          name: 'FUNCTIONS_WORKER_PROCESS_COUNT'
          value: '1'
        }
        {
          name: 'PYTHON_ENABLE_WORKER_EXTENSIONS'
          value: '1'
        }
      ]
      alwaysOn: false
      preWarmedInstanceCount: preWarmedInstanceCount
      ftpsState: 'Disabled'
      cors: {
        allowedOrigins: [
          'https://${appName}.${environment}.zimax.net'
          'https://localhost:5173'
        ]
        supportCredentials: false
      }
    }
  }
  tags: {
    environment: environment
    application: appName
  }
}

resource functionLogs 'Microsoft.Web/sites/config@2023-01-01' = {
  parent: functionApp
  name: 'logs'
  properties: {
    applicationLogs: {
      fileSystem: {
        level: 'Information'
      }
    }
  }
}

@description('Outputs the Function App hostname.')
output functionAppHostname string = functionApp.properties.defaultHostName

@description('Outputs the storage account resource id.')
output storageAccountId string = storage.id

@description('Outputs the Application Insights connection string.')
output appInsightsConnectionString string = appInsights.properties.ConnectionString
