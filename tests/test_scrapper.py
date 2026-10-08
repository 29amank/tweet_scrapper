"""Offline tests for the legacy Twitter/X search-export prototype.

No real credentials, Twitter/X API calls, or user records are involved.
"""
import csv
from datetime import datetime
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import scrapper


class TestTwitterScraper(unittest.TestCase):
    def test_missing_credentials_produce_clear_error(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "X_CONSUMER_KEY"):
                scrapper.build_api()

    def test_auth_uses_environment_credentials_without_network(self):
        variables = {
            "X_CONSUMER_KEY": "example-key",
            "X_CONSUMER_SECRET": "example-secret",
            "X_ACCESS_TOKEN": "example-token",
            "X_ACCESS_TOKEN_SECRET": "example-token-secret",
        }
        with patch.dict(os.environ, variables, clear=True):
            with patch("scrapper.tweepy.OAuth1UserHandler") as auth:
                with patch("scrapper.tweepy.API") as api:
                    result = scrapper.build_api()
        auth.assert_called_once_with(*variables.values())
        api.assert_called_once_with(auth.return_value)
        self.assertIs(result, api.return_value)

    def test_date_validation(self):
        self.assertTrue(scrapper.validate_date("2026-10-08"))
        self.assertFalse(scrapper.validate_date("2026-02-30"))
        self.assertFalse(scrapper.validate_date("08-10-2026"))

    def test_text_cleanup(self):
        value = scrapper.clean_text("Hello 🌎 https://example.org\n  world", auto_clean=True)
        self.assertEqual(value, "Hello world")
        self.assertEqual(scrapper.clean_text("A|B", custom_characters="|"), "AB")

    def test_json_export_uses_only_test_data(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "test-posts.json"
            scrapper.save_to_json([{"id": "synthetic"}], str(dest))
            self.assertEqual(json.loads(dest.read_text(encoding="utf-8")), [{"id": "synthetic"}])

    def test_csv_export_uses_only_test_data(self):
        tweet = SimpleNamespace(
            id_str="00001",
            user=SimpleNamespace(screen_name="synthetic_user"),
            created_at=datetime(2026, 10, 8, 9, 30),
            favorite_count=2,
            retweet_count=0,
            full_text="Example post",
        )
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "test-posts.csv"
            scrapper.save_to_csv([tweet], str(dest))
            with dest.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["tweet_id"], "00001")
        self.assertEqual(rows[0]["author"], "synthetic_user")
        self.assertEqual(rows[0]["text"], "Example post")


if __name__ == "__main__":
    unittest.main()
