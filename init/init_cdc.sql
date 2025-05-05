-- Create a dedicated user for Debezium
CREATE USER debezium WITH PASSWORD 'debezium';
ALTER USER debezium WITH SUPERUSER;

-- Create the sentiment_social table
CREATE TABLE IF NOT EXISTS public.sentiment_social (
    id SERIAL PRIMARY KEY,
    text TEXT,
    sentiment VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Set up logical replication
ALTER SYSTEM SET wal_level = logical;

-- Create publication for CDC
CREATE PUBLICATION sentiment_pub FOR TABLE public.sentiment_social;