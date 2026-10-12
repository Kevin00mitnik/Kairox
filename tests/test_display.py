import unittest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

import powerlens


class DisplayTests(unittest.TestCase):
    def render(self, *args):
        output = StringIO()
        with patch.object(
            powerlens,
            "console",
            Console(file=output, width=110, color_system=None, force_terminal=False),
        ):
            powerlens.show(*args)
        return output.getvalue()

    def test_renders_target_summary_and_findings(self):
        output = self.render(
            "example.com",
            {"high": ["admin.example.com"], "medium": ["api.example.com"], "low": ["www.example.com"]},
            [{"url": "https://www.example.com", "status": "[200]"}],
            ["443/tcp open https"],
            ["https://example.com/admin"],
            ["TLS 1.3 offered (OK)"],
            [],
        )

        self.assertIn("example.com", output)
        self.assertIn("Subdomains", output)
        self.assertIn("admin.example.com", output)
        self.assertIn("https://www.example.com", output)
        self.assertIn("TLS / SSL assessment", output)
        self.assertIn("All checks completed without reported errors.", output)

    def test_caps_long_sections_and_surfaces_check_errors(self):
        output = self.render(
            "example.com",
            {"high": [], "medium": [], "low": []},
            [],
            [],
            [f"https://example.com/page/{index}" for index in range(22)],
            [],
            ["Archived-URL check timed out"],
        )

        self.assertIn("Showing 20 of 22 entries", output)
        self.assertIn("Archived-URL check timed out", output)
        self.assertIn("Scan completed with checks requiring attention.", output)


if __name__ == "__main__":
    unittest.main()
