-- Initial database schema for Source AI MVP
-- Created: 2023-10-27
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Description: Creates the initial tables for users and photos services

-- Create database if it doesn't exist
-- Note: This might need to be run separately depending on your database setup
-- CREATE DATABASE IF NOT EXISTS source_ai_mvp;

-- Use the database
-- USE source_ai_mvp;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uid UUID NOT NULL DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    incentives_earned FLOAT,
    incentives_redeemed FLOAT,
    incentives_available FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create photos table
CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,
    uid UUID NOT NULL DEFAULT uuid_generate_v4(),
    title VARCHAR(255),
    description TEXT,
    filename VARCHAR(255) NOT NULL,
    original_key VARCHAR(500) NOT NULL,
    normalized_key TEXT,
    version_id VARCHAR(200),
    file_size INTEGER,
    mime_type VARCHAR(100),
    width INTEGER,
    height INTEGER,
    captured_at TIMESTAMP WITH TIME ZONE,
    sha256 BYTEA,
    face_valid BOOLEAN DEFAULT FALSE,
    face_match BOOLEAN,
    consent_version TEXT,
    monetizable BOOLEAN DEFAULT FALSE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

CREATE INDEX IF NOT EXISTS idx_photos_user_id ON photos(user_id);
CREATE INDEX IF NOT EXISTS idx_photos_created_at ON photos(created_at);
CREATE INDEX IF NOT EXISTS idx_photos_filename ON photos(filename);
CREATE INDEX IF NOT EXISTS idx_photos_originalkey_version ON photos(original_key, version_id);
CREATE INDEX IF NOT EXISTS idx_photos_user_created ON photos(user_id, created_at);

-- Create trigger to automatically update updated_at timestamp for users
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to photos table
DROP TRIGGER IF EXISTS update_photos_updated_at ON photos;
CREATE TRIGGER update_photos_updated_at
    BEFORE UPDATE ON photos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Consent ledger (versioned; revoke-compatible)
CREATE TABLE IF NOT EXISTS user_consent (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    scope TEXT NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (user_id, version)
);

-- Earnings: event-sourced
CREATE TABLE IF NOT EXISTS earning_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    photo_id INTEGER REFERENCES photos(id) ON DELETE SET NULL,
    amount_cents INT NOT NULL,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Earnings: aggregate balance
CREATE TABLE IF NOT EXISTS earning_balances (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    balance_cents BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Marketplace API clients
CREATE TABLE IF NOT EXISTS api_clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    scopes TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Access audit log
CREATE TABLE IF NOT EXISTS access_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_client_id UUID REFERENCES api_clients(id) ON DELETE SET NULL,
    user_id INTEGER,
    photo_id INTEGER,
    action TEXT NOT NULL,          -- e.g. SIGNED_URL_ISSUED
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_access_audit_created_at ON access_audit (created_at);

-- Insert sample data for development (optional)
-- Note: Remove this in production
INSERT INTO users (name, email, hashed_password) VALUES 
('John Doe', 'john@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4j8Q8x1v8y'),
('Jane Smith', 'jane@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4j8Q8x1v8y')
ON CONFLICT (email) DO NOTHING;

-- Note: The password hash above is for 'password123' - change this in production!
