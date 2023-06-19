FROM python:3.9.6-slim-buster as dev
RUN apt-get update -y && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install poetry==1.5.1
# Configuring poetry
RUN poetry config virtualenvs.create false
# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src
# Installing requirements
RUN poetry install
# Removing gcc
RUN apt-get purge -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
# Copying actual application
COPY . /app/src/
CMD ["uvicorn", "--host", "0.0.0.0", "app.main:app", "--reload"]
