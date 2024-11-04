# syntax=docker/dockerfile:1.7-labs
FROM python:3.12-slim-bookworm AS build

RUN apt-get update && apt-get install -y \
    tini

ARG VIRTUAL_ENV=/app/.venv

COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12

WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN uv sync --locked --no-cache --no-dev --no-install-project


#FROM python:3.12-slim-bookworm
# distroless is current 3.11, but the mismatch doesn't seem to matter
FROM gcr.io/distroless/python3-debian12

ARG COMMIT="(not set)"
ARG LASTMOD="(not set)"
ENV COMMIT=$COMMIT
ENV LASTMOD=$LASTMOD
ENV PYTHONUNBUFFERED=1

USER nonroot

WORKDIR /app/dist
COPY --chown=nonroot:nonroot ./src /app/dist
COPY --chown=nonroot:nonroot ./static /app/dist/static
COPY --chown=nonroot:nonroot --from=build /app/.venv/lib/python3.12/site-packages /app/dist

# in slim-bookworm: "/usr/local/bin/python3.12"
# in distroless:   "/usr/bin/python3.12"

ENV HOSTNAME 0.0.0.0
ENV PORT 4000
ENTRYPOINT [ \
  "/usr/bin/python3", \
  "serve.py" \
]
#ENTRYPOINT [ \
#  "/usr/bin/python3", \
#  "-m", "hypercorn", \
#  "--bind", "0.0.0.0:4000", \
#  "app:app" \
#]

# for slim-bookworm:
#WORKDIR /app
#ENTRYPOINT ["/app/.venv/bin/hypercorn", "src/app:app"]
