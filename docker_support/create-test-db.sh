#!/bin/bash
set -e

echo "Creating test database"
# Create the test database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    CREATE DATABASE "$POSTGRES_TEST_DB";
EOSQL
