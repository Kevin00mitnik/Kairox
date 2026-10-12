import asyncio
from utils.runner import run_cmd


async def get_subdomains(domain):
    output = await run_cmd(["subfinder", "-silent", "-d", domain])
    return sorted({line.strip() for line in output.splitlines() if line.strip()})