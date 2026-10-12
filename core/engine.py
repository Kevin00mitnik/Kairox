import asyncio

from modules.subdomain import get_subdomains
from modules.live import MAX_LIVE_HOSTS, get_live
from modules.ports import scan_ports
from modules.urls import get_urls
from modules.tls import check_tls
from core.analyzer import classify


async def run_engine(domain):
    subs = await get_subdomains(domain)
    categories = classify(subs)

    results = await asyncio.gather(
        get_live(subs),
        scan_ports(domain),
        get_urls(domain),
        check_tls(domain),
        return_exceptions=True,
    )

    names = ("Live-host check", "Port scan", "Archived-URL check", "TLS check")
    outputs = []
    errors = []
    for name, result in zip(names, results):
        if isinstance(result, Exception):
            outputs.append([])
            errors.append(f"{name}: {result}")
        else:
            outputs.append(result)

    unique_subs_count = len(set(subs))
    if unique_subs_count > MAX_LIVE_HOSTS:
        errors.append(
            "Live-host check: limited to the first "
            f"{MAX_LIVE_HOSTS} of {unique_subs_count} discovered hosts "
            "to keep the probe bounded."
        )

    live, ports, urls, tls = outputs
    return categories, live, ports, urls, tls, errors