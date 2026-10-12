import asyncio
import warnings

from utils.runner import run_cmd


async def get_subdomains(domain):
    commands = [
        ["subfinder", "-silent", "-d", domain],
        ["amass", "enum", "-passive", "-d", domain],
    ]

    results = await asyncio.gather(
        *(run_cmd(command) for command in commands),
        return_exceptions=True,
    )

    subs = set()
    errors = []
    for result in results:
        if isinstance(result, Exception):
            errors.append(str(result))
            continue
        subs.update(line.strip() for line in result.splitlines() if line.strip())

    if errors and not subs:
        raise RuntimeError("Subdomain discovery failed: " + "; ".join(errors))
    if errors:
        warnings.warn(
            "Some subdomain sources failed: " + "; ".join(errors),
            RuntimeWarning,
            stacklevel=2,
        )

    return list(subs)