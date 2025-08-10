-- db/init/01-init.sql
-- PostgreSQL initialization script

-- Create database if it doesn't exist (handled by Docker)
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For better indexing

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create indexes for better performance (will be created by Alembic, but good to have for reference)
-- These will be created after tables are created by migration

-- Full-text search indexes (can be added later)
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_projects_search 
-- ON projects USING gin(to_tsvector('english', title || ' ' || description));

-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_search 
-- ON user_profiles USING gin(to_tsvector('english', display_name || ' ' || COALESCE(bio, '')));

---

-- db/seeds/sample_data.sql
-- Additional SQL seed data if needed

-- Sample skill categories for projects
INSERT INTO skill_categories (name, description) VALUES 
('Web Development', 'Frontend and backend web development skills'),
('Mobile Development', 'iOS and Android app development'),
('Design', 'UI/UX design, graphic design, and visual arts'),
('Data Science', 'Data analysis, machine learning, and statistics'),
('Marketing', 'Digital marketing, content creation, and SEO'),
('Writing', 'Content writing, copywriting, and technical writing')
ON CONFLICT DO NOTHING;

-- Sample project categories
INSERT INTO project_categories (name, parent_id, description) VALUES 
('Technology', NULL, 'Technology and software development projects'),
('Design & Creative', NULL, 'Creative and design projects'),
('Marketing & Sales', NULL, 'Marketing and sales projects'),
('Writing & Content', NULL, 'Writing and content creation projects'),
('Business', NULL, 'Business and administrative projects')
ON CONFLICT DO NOTHING;