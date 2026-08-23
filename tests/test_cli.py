"""Tests for the helpdesk CLI."""

import subprocess
import sys
import unittest


class TestCLIList(unittest.TestCase):
    """Tests for the 'list' subcommand."""

    def run_cli(self, *args):
        """Helper to invoke the CLI as a subprocess."""
        result = subprocess.run(
            [sys.executable, "-m", "helpdesk", *args],
            capture_output=True,
            text=True,
            cwd=str(
                __import__("pathlib").Path(__file__).resolve().parent.parent
            ),
        )
        return result

    def test_list_shows_all_tickets(self):
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0)
        self.assertIn("INC-101", result.stdout)
        self.assertIn("INC-109", result.stdout)

    def test_list_shows_ticket_priority(self):
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0)
        # Output should contain priority labels
        self.assertIn("HIGH", result.stdout.upper())
        self.assertIn("LOW", result.stdout.upper())

    def test_list_returns_nonzero_on_unknown_command(self):
        result = self.run_cli("nonexistent")
        self.assertNotEqual(result.returncode, 0)


    def test_list_filters_by_priority(self):
        result = self.run_cli("list", "--priority", "high")
        self.assertEqual(result.returncode, 0)
        self.assertIn("INC-104", result.stdout)
        self.assertIn("INC-109", result.stdout)
        self.assertNotIn("INC-101", result.stdout)
        self.assertNotIn("INC-102", result.stdout)

    def test_invalid_priority_exits_nonzero(self):
        result = self.run_cli("list", "--priority", "urgent")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)
    def test_prio_alias_still_filters(self):
        result = self.run_cli("list", "--prio", "high")
        self.assertEqual(result.returncode, 0)
        self.assertIn("INC-104", result.stdout)
        self.assertNotIn("INC-101", result.stdout)
        
    def test_prio_alias_warns_about_deprecation(self):
        result = self.run_cli("list", "--prio", "high")
        self.assertEqual(result.returncode, 0)
        self.assertIn("deprecated", result.stderr)


    def test_list_filters_by_owner(self):
        result = self.run_cli("list", "--owner", "alex")
        self.assertEqual(result.returncode, 0)
        self.assertIn("INC-101", result.stdout)
        self.assertNotIn("INC-102", result.stdout)


if __name__ == "__main__":
    unittest.main()
