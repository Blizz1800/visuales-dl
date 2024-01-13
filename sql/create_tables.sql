CREATE TABLE IF NOT EXISTS "files" (
    id INTEGER NOT NULL,
    name TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    size INTEGER NOT NULL,
    fsize REAL NOT NULL,
    unit VARCHAR[3] NOT NULL,
    subfolder TEXT,
    basefolder TEXT NOT NULL,
    PRIMARY KEY(id AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "downloads" (
    id INTEGER NOT NULL,
    name TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    complete INTEGER NOT NULL,
    PRIMARY KEY(id AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "files_downloads" (
    file_id INTEGER NOT NULL,
    download_id INTEGER NOT NULL,
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (download_id) REFERENCES downloads(id),
    PRIMARY KEY(file_id, download_id)
);

CREATE TABLE IF NOT EXISTS "updates" (
    id INTEGER NOT NULL,
    name TEXT UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id AUTOINCREMENT)
);