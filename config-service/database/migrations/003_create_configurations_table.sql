-- Create configurations table
CREATE TABLE configurations (
    id VARCHAR(26) PRIMARY KEY,  -- ULID format
    application_id VARCHAR(26) NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(256) NOT NULL,
    comments VARCHAR(1024),
    config JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(application_id, name)  -- Ensure name is unique per application
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_configurations_application_id ON configurations(application_id);
CREATE INDEX IF NOT EXISTS idx_configurations_name ON configurations(name);
CREATE INDEX IF NOT EXISTS idx_configurations_created_at ON configurations(created_at);
CREATE INDEX IF NOT EXISTS idx_configurations_config ON configurations USING GIN(config);

-- Create trigger to automatically update updated_at timestamp
CREATE TRIGGER update_configurations_updated_at 
    BEFORE UPDATE ON configurations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
