"""Allow `python -m helpdesk` to run the CLI."""

from helpdesk.cli import main

raise SystemExit(main())
