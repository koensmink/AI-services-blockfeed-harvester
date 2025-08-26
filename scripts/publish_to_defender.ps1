# Requires: AzureAD App Registration with Graph API permissions (SecurityIncident.ReadWrite.All)

param(
    [string]$TenantId,
    [string]$ClientId,
    [string]$ClientSecret,
    [string]$FilePath = "output/defender_indicators.csv"
)

# Acquire token
$body = @{
    grant_type    = "client_credentials"
    client_id     = $ClientId
    client_secret = $ClientSecret
    scope         = "https://graph.microsoft.com/.default"
}
$tokenRequest = Invoke-RestMethod -Method Post -Uri "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token" -Body $body
$token = $tokenRequest.access_token

# Upload indicators
$indicators = Import-Csv $FilePath
foreach ($indicator in $indicators) {
    $body = @{
        indicatorType = $indicator.IndicatorType
        action = $indicator.Action
        value = $indicator.Value
        title = $indicator.Title
        description = $indicator.Description
        severity = $indicator.Severity
    } | ConvertTo-Json

    Invoke-RestMethod -Method Post `
        -Uri "https://graph.microsoft.com/beta/security/tiIndicators" `
        -Headers @{Authorization = "Bearer $token"; "Content-Type" = "application/json"} `
        -Body $body
}
publish_to_defender.ps1
