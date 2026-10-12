import unittest
from unittest.mock import AsyncMock, patch

from modules.subdomain import get_subdomains


class GetSubdomainsTests(unittest.IsolatedAsyncioTestCase):
    async def test_returns_sorted_unique_subdomains_and_ignores_empty_lines(self):
        with patch(
            "modules.subdomain.run_cmd",
            new=AsyncMock(return_value="www.example.com\n\napi.example.com\nwww.example.com\n"),
        ):
            results = await get_subdomains("example.com")

        self.assertEqual(results, ["api.example.com", "www.example.com"])

    async def test_uses_subfinder_for_subdomain_discovery(self):
        with patch(
            "modules.subdomain.run_cmd",
            new=AsyncMock(return_value="www.example.com\n"),
        ) as run_cmd:
            await get_subdomains("example.com")

        run_cmd.assert_awaited_once_with(["subfinder", "-silent", "-d", "example.com"])


if __name__ == "__main__":
    unittest.main()
