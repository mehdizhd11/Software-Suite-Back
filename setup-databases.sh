#!/bin/bash
# Setup script to create databases for Jira and Confluence

echo "Setting up databases for Jira and Confluence..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Create Jira database
docker exec -i postgres_db psql -U ${DATABASE_USER:-postgres} -c "CREATE DATABASE ${JIRA_DB_NAME:-jira};" 2>/dev/null || echo "Jira database already exists or error occurred"

# Create Confluence database
docker exec -i postgres_db psql -U ${DATABASE_USER:-postgres} -c "CREATE DATABASE ${CONFLUENCE_DB_NAME:-confluence};" 2>/dev/null || echo "Confluence database already exists or error occurred"

echo "Database setup complete!"
echo "Jira database: ${JIRA_DB_NAME:-jira}"
echo "Confluence database: ${CONFLUENCE_DB_NAME:-confluence}"

