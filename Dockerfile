FROM python:3.9.6-slim-buster as build
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install poetry
# Configuring poetry
RUN poetry config virtualenvs.create false
# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src
# Installing requirements
RUN poetry install --only main
# Removing gcc
RUN apt-get purge -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
# Copying actual application
COPY . /app/src/
RUN poetry install --only main

FROM build as dev
RUN poetry install
