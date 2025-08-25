FROM python:3.12.0-slim-bookworm AS stage1

FROM stage1 AS builder

WORKDIR /app

COPY pyproject.toml uv.lock /app/
# Install uv and dependencies
RUN pip install --no-cache-dir uv
RUN uv sync --locked --no-dev


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