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
    notes TEXT,
    latitude DOUBLE NOT NULL DEFAULT 0,
    longitude DOUBLE NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullName VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    count INT DEFAULT 0,
    userEmail VARCHAR(255) NOT NULL,
    contactEmail VARCHAR(255),
    contactPhone VARCHAR(50),
    notes TEXT,
    latitude DOUBLE NOT NULL DEFAULT 0,
    longitude DOUBLE NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prospectId INT,
    customerId INT,
    content TEXT NOT NULL,
    authorEmail VARCHAR(255) NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prospectId) REFERENCES prospects(id) ON DELETE CASCADE,
    FOREIGN KEY (customerId) REFERENCES customers(id) ON DELETE CASCADE,
    CHECK (
        (prospectId IS NOT NULL AND customerId IS NULL) OR
        (prospectId IS NULL AND customerId IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS knocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prospectId INT,
    customerId INT,
    date DATETIME NOT NULL,
    status VARCHAR(100) NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    userEmail VARCHAR(255) NOT NULL,
    FOREIGN KEY (prospectId) REFERENCES prospects(id) ON DELETE CASCADE,
    FOREIGN KEY (customerId) REFERENCES customers(id) ON DELETE CASCADE,
    CHECK (
        (prospectId IS NOT NULL AND customerId IS NULL) OR
        (prospectId IS NULL AND customerId IS NOT NULL)
    )
);