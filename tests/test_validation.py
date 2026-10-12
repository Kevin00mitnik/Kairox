import unittest

from utils.validation import normalize_domain


class NormalizeDomainTests(unittest.TestCase):
    def test_normalizes_domain(self):
        self.assertEqual(normalize_domain("  Example.COM. "), "example.com")

    def test_converts_international_domain_to_idna(self):
        self.assertEqual(normalize_domain("bücher.example"), "xn--bcher-kva.example")

    def test_accepts_ip_address(self):
        self.assertEqual(normalize_domain("192.0.2.1"), "192.0.2.1")

    def test_rejects_shell_metacharacters_and_urls(self):
        for value in ("example.com; whoami", "https://example.com", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_domain(value)


if __name__ == "__main__":
    unittest.main()
