## AI Feed structure

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
│  ├─ harvesters/
│  │  ├─ directories.py
│  │  ├─ crtsh.py
│  │  └─ github_topics.py
│  ├─ classify.py
│  ├─ verify.py
│  ├─ emitters.py
│  └─ util.py
└─ .github/workflows/update.yml
```
