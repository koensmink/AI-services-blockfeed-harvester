# WIP

## Hoe detecteren we nieuwe AI-diensten?

* Certificate Transparency (crt.sh): nieuwe AI-brands lekken vaak via CN/SAN (keywords + .ai-TLD bias).
* GitHub topics & README homepages: vroege adoptie signaal.
* AI-directory scrapes: Product Hunt / directories publiceren dagelijks nieuwe tools.
* Heuristieken: TLD .ai, subdomeinen met api, ai, gpt, content-woorden (“LLM”, “embeddings”, “text-to-image”, “prompt”).
* DNS-verificatie: alleen resolvables opnemen → minder rotzooi.
* Policy-overrides: allowlist.txt, denylist.txt.

## Gebruik in verschillende omgevingen

* DNS RPZ (Bind/Unbound/PowerDNS) -> Importeer output/rpz.zone als policy-zone en zet actie op CNAME . (NXDOMAIN).
* Pi-hole / AdGuard / OPNsense (pfBlockerNG) -> Voeg output/pi-hole.txt of pfblockerng.txt toe als custom list (HTTP-raw vanaf 	   	GitHub raw URL).
* Squid/Proxy -> Include output/squid_acl.conf (of maak granularere url_regex op paths zoals /chat /gpt /gemini).
* Microsoft Defender for Endpoint (Network Protection / Indicators) -> Importeer output/defender_indicators.csv als Custom Indicators (action “Alert” of “Block”). <-- Watch out, beta yet due Microsoft / Bing URL in file

## AI Feed structure

- `src/main.py`: scraper die AI-domeinen verzamelt
- `output/defender_indicators.csv`: MDE-compatible lijst
- `.github/workflows/update.yml`: GitHub Actions workflow
- `scripts/publish_to_defender.ps1`: upload script naar MDE via Graph API

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
