# BüZe Mittagstisch Notifier

This project automatically monitors the weekly Mittagstisch menu
of the Bürgerzentrum Ehrenfeld and sends notifications to a Telegram
channel whenever a new menu is available.

## Installing  dependencies: 
Dependencies are installed with `uv`. Use `uv sync` to
create a virtualenv in the `.venv` folder, and install the dependencies.
You can run commands in the virtualenv with `uv run ...` or activate the
virtualenv directly with `source .venv/bin/activate`.

BüZe Mittagstisch Notifier itself is also configured via environment variables.
There is a list of the needed variables in `development/example.env`.
You can copy this file to `.env` and fill in the blank variables.