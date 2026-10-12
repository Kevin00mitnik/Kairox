from utils.runner import run_cmd


MAX_LIVE_HOSTS = 250


async def get_live(subs):
    if not subs:
        return []

    hosts = sorted(set(subs))[:MAX_LIVE_HOSTS]
    output = await run_cmd(
        [
            "httpx",
            "-silent",
            "-status-code",
            "-title",
            "-timeout",
            "5",
            "-retries",
            "0",
            "-threads",
            "25",
            "-rate-limit",
            "25",
        ],
        input_text="\n".join(hosts) + "\n",
        timeout=120,
    )

    results = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1].startswith("["):
            results.append({
                "url": parts[0],
                "status": parts[1]
            })

    return results