"""Command-line interface for HelpDesk Lite."""

import argparse
import sys

from helpdesk.service import load_tickets

PRIORITIES = ("low", "medium", "high")


class DeprecatedAlias(argparse.Action):
    """Store a value and warn that the flag it arrived on is deprecated."""

    def __call__(self, parser, namespace, values, option_string=None):
        print(
            f"warning: {option_string} is deprecated, use --priority instead",
            file=sys.stderr,
        )
        setattr(namespace, self.dest, values)


def format_ticket(ticket):
    """Render a single ticket as one line of CLI output."""
    return f"{ticket.id}  {ticket.priority.upper()}  {ticket.summary}"


def cmd_list(args):
    """Print tickets, optionally narrowed to a single priority or owner."""
    tickets = load_tickets()
    if args.priority:
        tickets = [t for t in tickets if t.priority == args.priority]
    if args.owner:
        tickets = [t for t in tickets if t.owner == args.owner]
    for ticket in tickets:
        print(format_ticket(ticket))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="helpdesk", description="Support ticket CLI.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    list_parser = subcommands.add_parser("list", help="List support tickets")
    list_parser.add_argument(
        "--priority",
        choices=PRIORITIES,
        help="Show only tickets with this priority",
    )
    list_parser.add_argument(
        "--prio",
        dest="priority",
        choices=PRIORITIES,
        help="Deprecated alias for --priority",
        action=DeprecatedAlias,
    )
    list_parser.add_argument(
        "--owner",
        help="Show only tickets assigned to this owner",
    )
    list_parser.set_defaults(handler=cmd_list)

    return parser


def main(argv=None):
    """Entry point for the helpdesk CLI."""
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
