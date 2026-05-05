CREATE DATABASE IF NOT EXISTS noid_db;
USE noid_db;

CREATE TABLE IF NOT EXISTS users (
    pid VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    year VARCHAR(20),
    program VARCHAR(100),
    dob DATE
);

CREATE TABLE IF NOT EXISTS access_log (
    pid VARCHAR(50) PRIMARY KEY,
    access_count INT DEFAULT 0,
    last_generated_time DATETIME,
    week_number INT,
    FOREIGN KEY (pid) REFERENCES users(pid)
);

-- Sample Data
INSERT INTO users (pid, name, department, year, program, dob) 
VALUES 
('PID123', 'John Doe', 'Computer Science', '2024', 'B.Tech', '2000-01-15'),
('PID456', 'Jane Smith', 'Information Tech', '2025', 'B.Tech', '2001-05-20')
ON DUPLICATE KEY UPDATE name=VALUES(name);
