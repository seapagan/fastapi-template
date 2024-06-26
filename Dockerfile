FROM python:3.12-slim AS dev
RUN apt-get update -y && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install poetry==1.8.3
# Configuring poetry
RUN poetry config virtualenvs.create false
# Copying requirements of a project
COPY pyproject.toml poetry.lock README.md /app/src/
WORKDIR /app/src
# Installing requirements
RUN poetry install --no-root
# Removing gcc
RUN apt-get purge -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
# Copying actual application
COPY . /app/src/
ENV DOCKER_RUNNING=1
CMD ["uvicorn", "--host", "0.0.0.0", "--port","8001","app.main:app", "--reload"]
