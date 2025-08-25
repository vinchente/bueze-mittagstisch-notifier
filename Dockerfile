FROM python:3.12.0-slim-bookworm AS stage1

FROM stage1 AS builder

RUN --mount=type=secret,id=PYPI_URL,env=PIP_INDEX_URL pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock /app/
# Install application dependencies
RUN #apt-get update && apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential
RUN --mount=type=secret,id=PYPI_URL,env=UV_DEFAULT_INDEX \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


FROM stage1

RUN useradd --system --user-group --uid 1009 notifier
USER notifier

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY pyproject.toml pyproject.toml
COPY bueze_mittagstisch_notifier bueze_mittagstisch_notifier
COPY data data
COPY .env .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

CMD ["python", "-m", "bueze_mittagstisch_notifier.main"]