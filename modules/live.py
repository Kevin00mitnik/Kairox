from utils.runner import run_cmd


async def get_live(subs):
    if not subs:
        return []

    output = await run_cmd(
        ["httpx", "-silent", "-status-code", "-title"],
        input_text="\n".join(subs) + "\n",
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