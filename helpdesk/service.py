"""Service layer for loading and querying tickets."""

import json
from pathlib import Path

from helpdesk.models import Ticket

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tickets.json"


def load_tickets(path=DEFAULT_DATA_FILE):
    """Load tickets from a JSON file and return them as Ticket objects."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Ticket(**entry) for entry in raw]
