-- USERS TABLE
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT,
    role TEXT
);

-- EMPLOYEE TABLE
CREATE TABLE employye (
    eid INTEGER PRIMARY KEY AUTOINCREMENT,
    ename TEXT,
    edept TEXT,
    esalary INTEGER,
    ephone TEXT
);


