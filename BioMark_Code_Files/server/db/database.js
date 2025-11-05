const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');

// Ensure the db directory exists
if (!fs.existsSync(__dirname)) {
  fs.mkdirSync(__dirname, { recursive: true });
}

const dbPath = path.join(__dirname, 'app.sqlite');

// Open (or create) the SQLite database
const db = new Database(dbPath);

// Enable foreign-key constraints and create tables if they do not exist
// NOTE: since this file is imported once at server start-up, the schema check
// runs a single time and is effectively idempotent.
db.exec(`
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  session_id TEXT PRIMARY KEY,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS uploads (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  original_name TEXT NOT NULL,
  server_path TEXT NOT NULL,
  uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES users(session_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analyses (
  id TEXT PRIMARY KEY,
  upload_id TEXT NOT NULL,
  result_path TEXT,
  status TEXT DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (upload_id) REFERENCES uploads(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notification_subscriptions (
  id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL,
  email TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  sent_at DATETIME,
  error_message TEXT
);
`);

module.exports = db; 