import unittest
from unittest.mock import AsyncMock, patch

from modules.subdomain import get_subdomains


class GetSubdomainsTests(unittest.IsolatedAsyncioTestCase):
    async def test_combines_sources_and_ignores_empty_lines(self):
        with patch(
            "modules.subdomain.run_cmd",
            new=AsyncMock(
                side_effect=[
                    "www.example.com\n\napi.example.com\n",
                    "api.example.com\nmail.example.com\n",
                ]
            ),
        ):
            results = await get_subdomains("example.com")

        self.assertCountEqual(
            results,
            ["www.example.com", "api.example.com", "mail.example.com"],
        )

    async def test_fails_when_both_sources_fail(self):
        with patch(
            "modules.subdomain.run_cmd",
            new=AsyncMock(side_effect=RuntimeError("tool unavailable")),
        ):
            with self.assertRaisesRegex(RuntimeError, "Subdomain discovery failed"):
                await get_subdomains("example.com")


if __name__ == "__main__":
    unittest.main()
