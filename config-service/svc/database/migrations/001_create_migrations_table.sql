-- Create migrations table to track applied migrations
CREATE TABLE IF NOT EXISTS migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on version for faster lookups
CREATE INDEX IF NOT EXISTS idx_migrations_version ON migrations(version);
