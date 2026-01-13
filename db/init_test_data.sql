-- Insert test parent
-- Use password "testpass123" - properly hashed
INSERT INTO parent (email, password_hash, name) VALUES 
('parent@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/vCe.WKeZm.Ui8W6Iq', 'Test Parent');

-- Insert test child (assuming parent_id = 1)
INSERT INTO child (parent_id, name, device_name) VALUES 
(1, 'Test Child', 'Samsung Galaxy S21');

-- Insert blocked categories
INSERT INTO blocked_category (parent_id, category) VALUES 
(1, 'adult'),
(1, 'gambling');

-- Insert specific blocked URLs
INSERT INTO blocked_url (parent_id, url) VALUES 
(1, 'www.example-blocked.com'),
(1, 'www.another-blocked.com');

-- Insert test reports (assuming child_id = 1)
INSERT INTO report (child_id, website_url, screenshot_url) VALUES 
(1, 'www.blocked-site.com', 'https://example.com/screenshots/1.png'),
(1, 'www.casino-site.com', 'https://example.com/screenshots/2.png');