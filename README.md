## AI Feed structure

Harvesters – verzamelen domeinen uit meerdere bronnen (AI-directories, Product Hunt, Certificate Transparency, GitHub topics, eigen logs).
Normalizer – domeinextractie, lowercasing, punycode → unicode, PSL (eTLD+1).
Classifiers – heuristic om te bepalen of iets (waarschijnlijk) een AI-dienst is (brand-lexicon, content-scan, CT-cert namen, trefwoorden).
Verifiers – DNS-resolve (A/AAAA/CNAME), optioneel HTTP-banner check.
Emitters – genereren lijstformaten voor je web content filter / DNS / proxy.
Policy – allowlist/denylist, categorieën (LLM chat, beeld, code-assist, API, model-hosting).

- `src/main.py`: scraper die AI-domeinen verzamelt
- `output/defender_indicators.csv`: MDE-compatible lijst
- `.github/workflows/update.yml`: GitHub Actions workflow
- `scripts/publish_to_defender.ps1`: upload script naar MDE via Graph API
- `data/allowlist.txt`: domeinen die je nooit wilt blokkeren (bijv. bredere platformen zoals github.com, google.com als je niet breed wil blokkeren).
- `data/denylist.txt`: handmatige toevoegingen/overrides.
- `data/seed.txt` uitbreidbaar; dit dekt de usual suspects.
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

## Intune/MDE Checklist

- Zet **Network Protection** op *Block*
- Implementeer **Web Content Filtering** via MDE
- Koppel deze blocklist CSV aan je tenant via het script
- Test met een paar AI-sites (bv. `chat.openai.com`)

## Automatisering

De GitHub Action draait elke dag en werkt automatisch de domeinlijst bij.

