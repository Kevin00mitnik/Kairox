import unittest
from unittest.mock import AsyncMock, patch

from modules.urls import get_urls


class GetUrlsTests(unittest.IsolatedAsyncioTestCase):
    async def test_limits_gau_retries_and_returns_sensitive_urls(self):
        with patch(
            "modules.urls.run_cmd",
            new=AsyncMock(
                return_value=(
                    "https://example.com/about\n"
                    "https://example.com/admin\n"
                    "https://example.com/api/v1\n"
                )
            ),
        ) as run_cmd:
            urls = await get_urls("example.com")

        self.assertEqual(
            urls,
            ["https://example.com/admin", "https://example.com/api/v1"],
        )
        run_cmd.assert_awaited_once_with(
            [
                "gau",
                "--timeout",
                "15",
                "--retries",
                "1",
                "--threads",
                "5",
                "example.com",
            ],
            timeout=120,
        )


if __name__ == "__main__":
    unittest.main()
