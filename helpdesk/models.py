"""Data models for support tickets."""

from dataclasses import dataclass


@dataclass
class Ticket:
    id: str
    priority: str
    summary: str
    owner: str
    status: str
