import os

def emit_all(domains):
    os.makedirs("output", exist_ok=True)

    # Plain list
    with open("output/domains.txt", "w") as f:
        f.write("\n".join(domains))

    # Defender CSV
    with open("output/defender_indicators.csv", "w") as f:
        f.write("IndicatorType,Indicator,Action
")
        for d in domains:
            f.write(f"DomainName,{d},Block\n")

    # Pi-hole
    with open("output/pi-hole.txt", "w") as f:
        f.write("\n".join(domains))

    # Squid ACL
    with open("output/squid_acl.conf", "w") as f:
        for d in domains:
            f.write(f".{d}\n")
