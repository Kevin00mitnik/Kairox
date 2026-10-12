import unittest
from unittest.mock import AsyncMock, patch

from modules.live import MAX_LIVE_HOSTS, get_live


class GetLiveTests(unittest.IsolatedAsyncioTestCase):
    async def test_limits_httpx_runtime_and_host_count(self):
        hosts = [f"host-{index:03}.example.com" for index in range(MAX_LIVE_HOSTS + 1)]
        with patch("modules.live.run_cmd", new=AsyncMock(return_value="")) as run_cmd:
            result = await get_live(hosts)

        self.assertEqual(result, [])
        args, kwargs = run_cmd.await_args
        self.assertEqual(
            args[0],
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
        )
        self.assertEqual(kwargs["timeout"], 120)
        self.assertEqual(
            kwargs["input_text"],
            "\n".join(sorted(hosts)[:MAX_LIVE_HOSTS]) + "\n",
        )


if __name__ == "__main__":
    unittest.main()
