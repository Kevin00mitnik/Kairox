from utils.runner import CommandError, run_cmd


async def check_tls(domain):
    try:
        output = await run_cmd(
            [
                "testssl",
                "--warnings",
                "off",
                "--quiet",
                "--color",
                "0",
                "--ids-friendly",
                "--protocols",
                "--server-defaults",
                "--vulnerable",
                "--connect-timeout",
                "10",
                "--openssl-timeout",
                "10",
                f"{domain}:443",
            ],
            timeout=900,
        )
    except CommandError as exc:
        return [f"TLS check failed: {exc}"]

    findings = [line.strip() for line in output.splitlines() if line.strip()]
    return findings or ["testssl completed without text output."]
