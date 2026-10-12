import unittest
from unittest.mock import AsyncMock, patch

from modules.tls import check_tls
from utils.runner import CommandError


class CheckTlsTests(unittest.IsolatedAsyncioTestCase):
    async def test_runs_testssl_for_https_and_returns_findings(self):
        with patch(
            "modules.tls.run_cmd",
            new=AsyncMock(return_value="TLS 1.2 offered (OK)\nTLS 1.0 not offered (OK)\n"),
        ) as run_cmd:
            findings = await check_tls("example.com")

        self.assertEqual(
            findings,
            ["TLS 1.2 offered (OK)", "TLS 1.0 not offered (OK)"],
        )
        args = run_cmd.await_args
        self.assertIn("--protocols", args.args[0])
        self.assertIn("--vulnerable", args.args[0])
        self.assertEqual(args.args[0][-1], "example.com:443")
        self.assertEqual(args.kwargs["timeout"], 900)

    async def test_reports_tls_tool_failure_without_losing_other_scan_results(self):
        with patch(
            "modules.tls.run_cmd",
            new=AsyncMock(side_effect=CommandError("testssl timed out")),
        ):
            findings = await check_tls("example.com")

        self.assertEqual(findings, ["TLS check failed: testssl timed out"])


if __name__ == "__main__":
    unittest.main()
