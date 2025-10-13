FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Configure the Python directory so it is consistent
ENV UV_PYTHON_INSTALL_DIR=/python
# Only use the managed Python version
ENV UV_PYTHON_PREFERENCE=only-managed

# Install Python before the project for caching
RUN uv python install 3.13

WORKDIR /dist
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable
COPY . /dist
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM gcr.io/distroless/cc:debug

# Copy the Python version
COPY --from=builder --chown=python:python /python /python

WORKDIR /dist
# Copy the application and logging config from the builder
COPY --from=builder --chown=app:app /dist/.venv /dist/.venv
COPY --from=builder --chown=app:app /dist/app /dist/app

# Place executables in the environment at the front of the path
ENV PATH="/dist/.venv/bin:$PATH"

EXPOSE 8080

ENTRYPOINT [ "gunicorn", "app.main:app", "-b", "0.0.0.0:8080", "-w", "1","-k", "uvicorn.workers.UvicornWorker", "-t", "0", "--log-config", "./app/logging.config", "--log-level", "info"]
