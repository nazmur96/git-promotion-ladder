"""Tests for the ticket service layer."""

import unittest
from pathlib import Path

from helpdesk.models import Ticket
from helpdesk.service import load_tickets


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tickets.json"


class TestLoadTickets(unittest.TestCase):
    """Tests for loading tickets from JSON."""

    def test_load_returns_list_of_tickets(self):
        tickets = load_tickets(DATA_FILE)
        self.assertIsInstance(tickets, list)
        self.assertTrue(len(tickets) > 0)
        self.assertIsInstance(tickets[0], Ticket)

    def test_load_parses_all_fields(self):
        tickets = load_tickets(DATA_FILE)
        ticket = next(t for t in tickets if t.id == "INC-104")
        self.assertEqual(ticket.priority, "high")
        self.assertEqual(ticket.summary, "Payment page returns an error")
        self.assertEqual(ticket.owner, "sam")
        self.assertEqual(ticket.status, "open")

    def test_load_returns_correct_count(self):
        tickets = load_tickets(DATA_FILE)
        self.assertEqual(len(tickets), 5)


if __name__ == "__main__":
    unittest.main()
