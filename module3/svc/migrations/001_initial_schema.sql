-- Initial schema for Configuration Service
-- Creates applications and configurations tables with ULID primary keys

-- Create applications table
CREATE TABLE applications (
    id VARCHAR(26) PRIMARY KEY,  -- ULID string format
    name VARCHAR(256) UNIQUE NOT NULL,
    comments VARCHAR(1024),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create configurations table
CREATE TABLE configurations (
    id VARCHAR(26) PRIMARY KEY,  -- ULID string format
    application_id VARCHAR(26) NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(256) NOT NULL,
    comments VARCHAR(1024),
    config JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(application_id, name)  -- Unique name per application
);

-- Create indexes for better performance
CREATE INDEX idx_configurations_application_id ON configurations(application_id);
CREATE INDEX idx_configurations_name ON configurations(name);
CREATE INDEX idx_configurations_config ON configurations USING GIN(config);

-- Create migrations tracking table
CREATE TABLE migrations (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    executed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Insert this migration record
INSERT INTO migrations (filename) VALUES ('001_initial_schema.sql');