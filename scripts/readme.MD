## Azure AD App Registration (voor Defender API)

Om het script `publish_to_defender.ps1` te gebruiken moet je een App Registration maken in Azure AD.

### Stappen:
1. Ga naar [Azure Portal](https://portal.azure.com) → **Azure Active Directory** → **App registrations**
2. Klik op **New registration**
   - Naam: `AI-Domain-Blockfeed`
   - Supported account types: *Single tenant* (aanbevolen)
   - Redirect URI: leeg laten
   - Klik **Register**
3. Noteer **Application (client) ID** en **Directory (tenant) ID**
4. Ga naar **Certificates & secrets** → Maak een nieuwe **Client secret**
   - Noteer de secret-waarde (wordt maar 1x getoond!)
5. Ga naar **API Permissions**
   - Klik **Add a permission** → **Microsoft Graph**
   - Kies **Application permissions**
   - Voeg toe: `SecurityThreatIndicators.ReadWrite.OwnedBy`
   - Klik **Grant admin consent**
6. Gebruik deze waarden in je PowerShell script:

```powershell
.\scripts\publish_to_defender.ps1 `
  -TenantId "<tenant-id>" `
  -ClientId "<client-id>" `
  -ClientSecret "<client-secret>"
```

