CREATE DATABASE IAPP;

-- Usar la base de datos
USE IAPP;

-- =======================================
-- TABLA DE ARTISTAS
-- =======================================
CREATE TABLE artists (
    artist_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- =======================================
-- TABLA DE CANCIONES (TRACKS)
-- =======================================
CREATE TABLE tracks (
    track_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    artist_id INT NOT NULL,
    album_name VARCHAR(255),
    release_date DATE,
    duration_ms INT,
    key_signature INT,
    mode TINYINT,
    popularity INT,
    genres VARCHAR(MAX),
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);

-- =======================================
-- TABLA DE CARACTERÍSTICAS DE AUDIO
-- =======================================
CREATE TABLE audio_features (
    track_id VARCHAR(50) PRIMARY KEY,
    energy FLOAT,
    tempo FLOAT,
    danceability FLOAT,
    loudness FLOAT,
    liveness FLOAT,
    valence FLOAT,
    speechiness FLOAT,
    instrumentalness FLOAT,
    acousticness FLOAT,
    FOREIGN KEY (track_id) REFERENCES tracks(track_id)
);

-- =======================================
-- TABLA DE HISTORIAL DE CONVERSACIONES
-- =======================================
CREATE TABLE conversation_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    timestamp DATETIME DEFAULT GETDATE(),
    session_id TEXT NOT NULL,
    user_prompt NVARCHAR(MAX) NOT NULL,
    ai_response NVARCHAR(MAX) NOT NULL
);