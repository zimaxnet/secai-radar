using '../main.bicep'

param resourceGroupName = 'secai-radar-dev-rg'
param location = 'eastus2'
param environment = 'dev'
param appName = 'secai-radar'
param functionContainerImage = 'zimaxnet/secai-radar-api:dev-latest'
param functionPlanSkuName = 'EP1'
param preWarmedInstanceCount = 0
param maximumElasticWorkerCount = 5
param storageAccountName = 'secairadardevsa'
param appInsightsDailyCapGb = 1
param appInsightsSamplingPercentage = 5
param postgresAdminPassword = 'SecureP@ssw0rd2024!' // IMPORTANT: Change this to a secure password in production
