CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
  username TEXT NOT NULL UNIQUE, hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS history (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  user_id INTEGER NOT NULL, 
  title TEXT NOT NULL, 
  [key] TEXT UNIQUE, 
  lang TEXT, 
  code TEXT NOT NULL, 
  pw TEXT, 
  time TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
  pw_req NUMERIC (1) DEFAULT (0) NOT NULL, 
  FOREIGN KEY (user_id) REFERENCES users (id)
);

