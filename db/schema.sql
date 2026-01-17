-- Al-Haris Database Schema

-- Parent account
CREATE TABLE parent (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Child account (linked to parent)
CREATE TABLE child (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES parent(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    device_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports from child device
CREATE TABLE report (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL REFERENCES child(id) ON DELETE CASCADE,
    website_url VARCHAR(500) NOT NULL,
    screenshot_url VARCHAR(500),  -- URL where screenshot is stored
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Category-based blocking (per parent, applies to all their children)
CREATE TABLE blocked_category (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES parent(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,     -- 'adult', 'gambling', 'social_media', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_id, category)
);

-- Specific URL blocking (per parent)
CREATE TABLE blocked_url (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES parent(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_id, url)
);

CREATE TABLE verification_code (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES parent(id) ON DELETE CASCADE,
    code VARCHAR(10) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master blacklist from UT1 (loaded once at deployment)
CREATE TABLE blacklist_domain (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,  -- 'adult', 'gambling', 'malware', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Indexes for common queries
CREATE INDEX idx_child_parent ON child(parent_id);
CREATE INDEX idx_report_child ON report(child_id);
CREATE INDEX idx_report_timestamp ON report(timestamp);
CREATE INDEX idx_blocked_category_parent ON blocked_category(parent_id);
CREATE INDEX idx_blocked_url_parent ON blocked_url(parent_id);
CREATE INDEX idx_verification_code_parent ON verification_code(parent_id);
CREATE INDEX idx_verification_code_expires ON verification_code(expires_at);
CREATE INDEX idx_blacklist_domain ON blacklist_domain(domain);
CREATE INDEX idx_blacklist_category ON blacklist_domain(category);