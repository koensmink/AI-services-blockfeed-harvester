import re, time
from pathlib import Path
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
import tldextract
import dns.resolver

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
OUT = BASE / "output"
OUT.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent":"ai-blockfeed-intune/1.0"}

# ---------------- Utils ----------------

def e2ld(domain: str) -> str:
    ext = tldextract.extract(domain)
    if not ext.suffix:
        return domain.lower()
    return f"{ext.domain}.{ext.suffix}".lower()

_defresolver = dns.resolver.Resolver()
_defresolver.lifetime = 3
_defresolver.timeout = 3


def resolvable(domain: str) -> bool:
    try:
        _defresolver.resolve(domain, "A")
        return True
    except Exception:
        try:
            _defresolver.resolve(domain, "AAAA")
            return True
        except Exception:
            return False


def http_get(url, timeout=15):
    return requests.get(url, timeout=timeout, headers=UA)


def domain_from_url(url: str) -> str | None:
    m = re.match(r"https?://([^/]+)", url)
    return m.group(1).split(":")[0].lower() if m else None

# ---------------- Harvesters ----------------

def harvest_directories():
    sources = [
        "https://theresanaiforthat.com/",
        "https://www.producthunt.com/topics/artificial-intelligence",
    ]
    found = set()
    for src in sources:
        try:
            r = http_get(src)
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http"):
                    d = domain_from_url(href)
                    if d: found.add(d)
        except Exception:
            continue
    return found


def harvest_crtsh(keywords=(
    "ai","gpt","llm","claude","gemini","copilot","mistral","grok",
    "perplexity","huggingface","stability","midjourney","replicate","cohere"
)):
    found = set()
    for kw in keywords:
        try:
            r = http_get(f"https://crt.sh/?q={kw}&output=json")
            if r.status_code != 200:
                time.sleep(2); continue
            for row in r.json():
                name_value = row.get("name_value","")
                for cn in name_value.split("\n"):
                    if "." in cn and not cn.startswith("*."):
                        found.add(cn.strip().lower())
            time.sleep(1.2)
        except Exception:
            time.sleep(1); continue
    return found


def harvest_github_topics():
    topics = ["chatgpt","llm","large-language-model","gpt","generative-ai","ai-assistant"]
    found = set()
    for t in topics:
        try:
            r = http_get(f"https://github.com/topics/{t}")
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http"):
                    d = domain_from_url(href)
                    if d: found.add(d)
        except Exception:
            continue
    return found

# ---------------- Classifier ----------------

BRAND_KEYWORDS = [
    "openai","chatgpt","oai","gpt","llm","anthropic","claude","gemini",
    "copilot","mistral","perplexity","stability","sdxl","midjourney","runway",
    "replicate","huggingface","x.ai","grok","cohere","meta ai","genai","rag",
    "embedding","text-to-image","speech-to-text","tts api","ai assistant"
]


def score_domain(domain: str) -> float:
    score = 0.0
    d = domain.lower()
    if d.endswith(".ai"): score += 0.5
    for kw in ["ai","gpt","llm","rag","embed","genai"]:
        if kw in d: score += 0.3
    try:
        r = http_get("https://" + d)
        if r.ok:
            txt = (r.text[:4000] or "").lower()
            m = re.search(r"<title>(.*?)</title>", txt, re.S)
            title = m.group(1) if m else ""
            bag = title + " " + txt
            for kw in BRAND_KEYWORDS:
                if kw in bag: score += 0.2
            if any(s in bag for s in ["api key","rest api","sdk","rate limit"]):
                score += 0.2
    except Exception:
        pass
    return min(score, 3.0)

# ---------------- Emitters ----------------

def write(path: Path, content: str):
    path.write_text(content + ("\n" if not content.endswith("\n") else ""), encoding="utf-8")


def emit_plain(domains):
    write(OUT / "domains.txt", "\n".join(sorted(domains)))


def emit_rpz(domains, zone="ai-block.local"):
    lines = [
        "$TTL 2h",
        "@   IN  SOA localhost. root.localhost. ( 1 1h 15m 30d 2h )",
        "    IN  NS  localhost.",
    ]
    for d in sorted(domains):
        lines.append(f"{d}. IN CNAME .")
    write(OUT / "rpz.zone", "\n".join(lines))


def emit_pihole(domains):
    write(OUT / "pi-hole.txt", "\n".join(sorted(domains)))


def emit_pfblockerng(domains):
    write(OUT / "pfblockerng.txt", "\n".join(sorted(domains)))


def emit_squid_acl(domains):
    # Basale host block; voor Big Tech liever URL‐granulariteit
    conf = "acl ai_sites dstdomain " + " ".join(sorted(domains)) + "\nhttp_access deny ai_sites\n"
    write(OUT / "squid_acl.conf", conf)


def emit_defender_csv(domains):
    """CSV voor Custom Indicators (Domains) in Defender portal of API‐import.
    Kolommen: IndicatorType,IndicatorValue,Action,Title,Description,Severity
    """
    rows = ["IndicatorType,IndicatorValue,Action,Title,Description,Severity"]
    for d in sorted(domains):
        rows.append(f"Domain,{d},Block,AI Domain Block,{d},Informational")
    write(OUT / "defender_indicators.csv", "\n".join(rows))

# ---------------- Main ----------------

def load_list(p: Path) -> set[str]:
    if not p.exists():
        return set()
    return set(l.strip().lower() for l in p.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#"))


def main():
    seed = load_list(DATA / "seed.txt")
    allow = load_list(DATA / "allowlist.txt")
    deny = load_list(DATA / "denylist.txt")

    candidates = set(seed)
    candidates |= harvest_directories()
    candidates |= harvest_crtsh()
    candidates |= harvest_github_topics()

    # normaliseren naar eTLD+1
    normalized = set(e2ld(c) for c in candidates if "." in c)

    # verify + score
    final = set()
    for d in normalized:
        if d in allow:
            continue
        if not resolvable(d):
            continue
        s = 0.0
        try:
            s = score_domain(d)
        except Exception:
            s = 0.0
        if (s >= 0.9) or (d in seed) or (d in deny):
            final.add(d)

    final |= deny
    final -= allow

    emit_plain(final)
    emit_rpz(final)
    emit_pihole(final)
    emit_pfblockerng(final)
    emit_squid_acl(final)
    emit_defender_csv(final)

    print(f"[+] Total domains: {len(final)}")

if __name__ == "__main__":
    main()
