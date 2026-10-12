import unittest
from unittest.mock import AsyncMock, patch

from core.engine import run_engine


class RunEngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_includes_tls_results_with_existing_scan_results(self):
        with (
            patch("core.engine.get_subdomains", new=AsyncMock(return_value=["www.example.com"])),
            patch("core.engine.get_live", new=AsyncMock(return_value=[{"url": "https://www.example.com", "status": "[200]"}])),
            patch("core.engine.scan_ports", new=AsyncMock(return_value=["443/tcp open https"])),
            patch("core.engine.get_urls", new=AsyncMock(return_value=["https://www.example.com/login"])),
            patch("core.engine.check_tls", new=AsyncMock(return_value=["TLS 1.2 offered (OK)"])),
        ):
            result = await run_engine("example.com")

        self.assertEqual(result[1], [{"url": "https://www.example.com", "status": "[200]"}])
        self.assertEqual(result[2], ["443/tcp open https"])
        self.assertEqual(result[3], ["https://www.example.com/login"])
        self.assertEqual(result[4], ["TLS 1.2 offered (OK)"])
        self.assertEqual(result[5], [])

    async def test_reports_a_failed_check_and_preserves_other_results(self):
        with (
            patch("core.engine.get_subdomains", new=AsyncMock(return_value=["www.example.com"])),
            patch("core.engine.get_live", new=AsyncMock(return_value=[{"url": "https://www.example.com", "status": "[200]"}])),
            patch("core.engine.scan_ports", new=AsyncMock(return_value=["443/tcp open https"])),
            patch("core.engine.get_urls", new=AsyncMock(side_effect=RuntimeError("archive timed out"))),
            patch("core.engine.check_tls", new=AsyncMock(return_value=["TLS 1.2 offered (OK)"])),
        ):
            result = await run_engine("example.com")

        self.assertEqual(result[1], [{"url": "https://www.example.com", "status": "[200]"}])
        self.assertEqual(result[2], ["443/tcp open https"])
        self.assertEqual(result[3], [])
        self.assertEqual(result[4], ["TLS 1.2 offered (OK)"])
        self.assertEqual(result[5], ["Archived-URL check: archive timed out"])

    async def test_reports_when_live_host_probe_is_capped(self):
        subs = [f"host-{index}.example.com" for index in range(251)]
        with (
            patch("core.engine.get_subdomains", new=AsyncMock(return_value=subs)),
            patch("core.engine.get_live", new=AsyncMock(return_value=[])),
            patch("core.engine.scan_ports", new=AsyncMock(return_value=[])),
            patch("core.engine.get_urls", new=AsyncMock(return_value=[])),
            patch("core.engine.check_tls", new=AsyncMock(return_value=[])),
        ):
            result = await run_engine("example.com")

        self.assertEqual(
            result[5],
            [
                "Live-host check: limited to the first 250 of 251 discovered hosts "
                "to keep the probe bounded."
            ],
        )


if __name__ == "__main__":
    unittest.main()
