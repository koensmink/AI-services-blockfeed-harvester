import re, json, time, socket
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

# ---------- Utils ----------
PSL_CACHE = {}

def e2ld(domain: str) -> str:
    ext = tldextract.extract(domain)
    if not ext.suffix:
        return domain.lower()
    return f"{ext.domain}.{ext.suffix}".lower()

def domain_from_url(url: str) -> str | None:
    m = re.match(r"https?://([^/]+)", url)
    return m.group(1).split(":")[0].lower() if m else None

def http_get(url, timeout=15):
    return requests.get(url, timeout=timeout, headers={"User-Agent":"ai-blockfeed/1.0"})

# ---------- Harvesters ----------
def harvest_directories():
    """
    Scrape simpele AI directories en productpagina's als bron voor nieuwe domeinen.
    """
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

def harvest_crtsh(keywords=("ai","gpt","llm","claude","gemini","copilot","mistral","grok","perplexity","huggingface","stability","midjourney","replicate","cohere")):
    """
    Query crt.sh per keyword op CN/SAN. Simpele JSON endpoint.
    NB: publiek rate-limited;
    """
    found = set()
    for kw in keywords:
        try:
            r = http_get(f"https://crt.sh/?q={kw}&output=json")
            if r.status_code != 200: 
                time.sleep(2)
                continue
            for row in r.json():
                name_value = row.get("name_value","")
                for cn in name_value.split("\n"):
                    if "." in cn and not cn.startswith("*."):
                        found.add(cn.strip().lower())
            time.sleep(1.2)
        except Exception:
            time.sleep(1)
            continue
    return found

def harvest_github_topics():
    """
    Heel eenvoudige scraper op GitHub topic pagina's om homepages te vinden.
    """
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

# ---------- Classifier ----------
BRAND_KEYWORDS = [
    # merknamen & generiek
    "openai","chatgpt","oai","gpt","llm","anthropic","claude","gemini","copilot","mistral","perplexity",
    "stability","sdxl","midjourney","runway","replicate","huggingface","x.ai","grok","cohere","meta ai",
    "ai assistant","genai","rag","embedding","text-to-image","image generation","speech-to-text","tts api"
]

def score_domain(domain: str) -> float:
    score = 0.0
    d = domain.lower()
    # basic heuristics
    if d.endswith(".ai"): score += 0.5
    for kw in ["ai","gpt","llm","rag","embed","genai"]:
        if kw in d: score += 0.3
    # content sniff
    try:
        r = http_get("https://" + d)
        txt = (r.text[:4000] or "").lower()
        title = ""
        m = re.search(r"<title>(.*?)</title>", txt, re.S)
        if m: title = m.group(1)
        bag = title + " " + txt
        for kw in BRAND_KEYWORDS:
            if kw in bag:
                score += 0.2
        # API-signalen
        if any(s in bag for s in ["api key","rest api","sdk","rate limit"]):
            score += 0.2
    except Exception:
        pass
    return min(score, 3.0)

# ---------- Verify ----------
def resolvable(domain: str) -> bool:
    try:
        dns.resolver.resolve(domain, "A", lifetime=3)
        return True
    except Exception:
        try:
            dns.resolver.resolve(domain, "AAAA", lifetime=3)
            return True
        except Exception:
            return False

# ---------- Emitters ----------
def emit_plain(domains):
    (OUT / "domains.txt").write_text("\n".join(sorted(domains)) + "\n")

def emit_rpz(domains, zone="ai-block.local"):
    lines = [
        f"$TTL 2h",
        f"@   IN  SOA localhost. root.localhost. ( 1 1h 15m 30d 2h )",
        f"    IN  NS  localhost.",
    ]
    for d in sorted(domains):
        lines.append(f"{d}. IN CNAME .")
    (OUT / "rpz.zone").write_text("\n".join(lines) + "\n")

def emit_pihole(domains):
    # gravity adlist format
    (OUT / "pi-hole.txt").write_text("\n".join(sorted(domains)) + "\n")

def emit_pfblockerng(domains):
    # één domein per regel
    (OUT / "pfblockerng.txt").write_text("\n".join(sorted(domains)) + "\n")

def emit_squid_acl(domains):
    # host_regex ACL (let op: brede domeinen kunnen collateral damage geven)
    pats = [rf"\.{re.escape(d)}$" for d in sorted(domains)]
    (OUT / "squid_acl.conf").write_text("acl ai_sites dstdomain " + " ".join(sorted(domains)) + "\nhttp_access deny ai_sites\n")

def emit_defender(domains):
    """
    Microsoft Defender custom indicators CSV.
    Columns: IndicatorType,IndicatorValue,Action,Title,Description,Severity
    """
    rows = ["IndicatorType,IndicatorValue,Action,Title,Description,Severity"]
    for d in sorted(domains):
        rows.append(f"Domain,{d},Alert,AI Domain Block,{d},Informational")
    (OUT / "defender_indicators.csv").write_text("\n".join(rows) + "\n")

# ---------- Main ----------
def load_list(p: Path) -> set[str]:
    return set(l.strip().lower() for l in p.read_text().splitlines() if l.strip() and not l.startswith("#"))

def main():
    seed = load_list(DATA / "seed.txt")
    allow = load_list(DATA / "allowlist.txt") if (DATA / "allowlist.txt").exists() else set()
    deny = load_list(DATA / "denylist.txt") if (DATA / "denylist.txt").exists() else set()

    candidates = set(seed)
    # harvest
    candidates |= harvest_directories()
    candidates |= harvest_crtsh()
    candidates |= harvest_github_topics()

    # normaliseren -> eTLD+1
    normalized = set(e2ld(c) for c in candidates if "." in c)

    # verify + classify
    scored = []
    for d in normalized:
        if d in allow: 
            continue
        ok = resolvable(d)
        s = score_domain(d) if ok else 0.0
        if ok and (s >= 0.9 or d in deny or d in seed):
            scored.append((d, s))

    final = set(d for d, s in scored)
    # policy
    final |= deny
    final -= allow

    # outputs
    emit_plain(final)
    emit_rpz(final)
    emit_pihole(final)
    emit_pfblockerng(final)
    emit_squid_acl(final)
    emit_defender(final)

    print(f"[+] Total domains: {len(final)}")

if __name__ == "__main__":
    main()
