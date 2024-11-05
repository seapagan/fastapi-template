FROM python:3.12-slim AS dev
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update -y && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copying requirements of a project
COPY pyproject.toml uv.lock README.md /app/src/
WORKDIR /app

# Install dependencies
ENV UV_SYSTEM_PYTHON=1
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy the project into the image
COPY . /app/
# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"
ENV DOCKER_RUNNING=1

# Running the application
CMD ["uvicorn", "--host", "0.0.0.0", "--port","8001","app.main:app", "--reload"]
