#!/bin/sh

# # Wait for the database to be available
# echo "Waiting for database to be ready..."
# until psql -h database -U postgres -d xero -c "SELECT 1" > /dev/null 2>&1; do
#     sleep 2
# done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting FastAPI server with Uvicorn..."
uvicorn main:app --host 0.0.0.0 --port 8000