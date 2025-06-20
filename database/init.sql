-- ./database/init.sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS prospects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullName VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    count INT DEFAULT 0,
    list VARCHAR(50) DEFAULT 'Prospects',
    userEmail VARCHAR(255) NOT NULL,
    contactEmail VARCHAR(255),
    contactPhone VARCHAR(50),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prospectId INT NOT NULL,
    content TEXT NOT NULL,
    authorEmail VARCHAR(255) NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prospectId) REFERENCES prospects(id) ON DELETE CASCADE
);