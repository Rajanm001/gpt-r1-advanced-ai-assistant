-- Database initialization script
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE gpt_r1_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gpt_r1_db');

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE gpt_r1_db TO postgres;

-- Create extension for UUID generation
\c gpt_r1_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema for application
CREATE SCHEMA IF NOT EXISTS chatgpt_app;