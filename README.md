laatste status scraper: [![Update AI Blockfeed](https://github.com/koensmink/AI-services-blockfeed-harvester/actions/workflows/update.yml/badge.svg?event=workflow_dispatch)](https://github.com/koensmink/AI-services-blockfeed-harvester/actions/workflows/update.yml)

# Ai url scraper
---
Dit project houdt automatisch lijsten bij van AI-gerelateerde websites, sorteert ze (zo nodig) voor verschillende beveiligings-tools, en zorgt ervoor dat die lijsten dagelijks automatisch worden bijgewerkt en gepusht naar Microsoft Defender. Ideaal voor die willen beheren wat er op het netwerk geblokkeerd of toegestaan wordt — zonder zelf dagelijks handmatig in te grijpen.

## AI Feed structuur
---
De AI structuur van de folders in deze repo staan in het onderstaande overzicht toegelicht in wat ze doen. 

- `src/main.py` Scraper die AI-domeinen verzamelt
- `.github/workflows/update.yml` GitHub Actions workflow
- `scripts/publish_to_defender.ps1` Upload script naar MDE via Graph API
- `data/allowlist.txt` Domeinen die je nooit wilt blokkeren (bijv. bredere platformen google,bing,microsoft).
- `data/denylist.txt` Handmatige toevoegingen/overrides.
- `data/seed.txt` Uitbreidbaar; dit dekt de usual suspects.
- `output/domains.txt` Raw formaat om als universele bron te gebruiken. Geen layout. 
- `output/rpz.zone` Bind/Unbound/PowerDNS importeer output/rpz.zone als policy-zone en zet actie op CNAME (NXDOMAIN).
- `output/pi-hole.txt` Pi-hole / AdGuard / OPNsense Voeg output/pi-hole.txt toe als custom list (HTTP-raw vanaf GitHub raw URL).
- `output/pfblockerng.txt` PfBlockerNG Voeg pfblockerng.txt toe als custom list (HTTP-raw vanaf GitHub raw URL). 
- `output/squid_acl.conf` Squid/Proxy Include output/squid_acl.conf (of maak granularere url_regex op paths zoals /chat /gpt /gemini).
- `output/defender_indicators.csv`: MDE-compatible lijst

```
ai-blockfeed/
├─ data/
│  ├─ seed.txt
│  ├─ allowlist.txt
│  └─ denylist.txt
├─ output/
│  ├─ domains.txt
│  ├─ rpz.zone
│  ├─ pi-hole.txt
│  ├─ pfblockerng.txt
│  ├─ squid_acl.conf
│  └─ defender_indicators.csv
├─ src/
│  ├─ main.py
└─ .github/workflows/update.yml
```

## Automatisering

De GitHub Action draait elke dag (04:05 AM) en werkt automatisch de domeinlijst bij.
