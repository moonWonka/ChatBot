-- Eliminar tablas en orden inverso a la creación, para evitar dependencias
DROP TABLE IF EXISTS audio_features;
DROP TABLE IF EXISTS tracks;
DROP TABLE IF EXISTS conversation_history; -- Agregada para completar
DROP TABLE IF EXISTS artists;


-- Crear la base de datos
CREATE DATABASE IAPP;

-- Usar la base de datos
USE IAPP;

-- =======================================
-- TABLA DE ARTISTAS
-- =======================================
CREATE TABLE artists (
    artist_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL UNIQUE
);

-- =======================================
-- TABLA DE CANCIONES (TRACKS)
-- =======================================
CREATE TABLE tracks (
    track_id NVARCHAR(50) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    artist_id INT NOT NULL,
    album_name NVARCHAR(255),
    release_date DATE,
    duration_ms INT,
    key_signature INT,
    mode INT,
    popularity INT,
    genres NVARCHAR(MAX),
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);

-- =======================================
-- TABLA DE CARACTERÍSTICAS DE AUDIO
-- =======================================
CREATE TABLE audio_features (
    track_id NVARCHAR(50) PRIMARY KEY,
    energy DECIMAL(5,3),
    tempo DECIMAL(6,2),
    danceability DECIMAL(5,3),
    loudness DECIMAL(7,3),
    liveness DECIMAL(5,3),
    valence DECIMAL(5,3),
    speechiness DECIMAL(5,3),
    instrumentalness DECIMAL(5,3),
    acousticness DECIMAL(5,3),
    FOREIGN KEY (track_id) REFERENCES tracks(track_id)
);

-- =======================================
-- TABLA DE HISTORIAL DE CONVERSACIONES
-- =======================================
CREATE TABLE conversation_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    timestamp DATETIME DEFAULT GETDATE(),
    session_id NVARCHAR(50) NOT NULL,
    user_prompt NVARCHAR(MAX) NOT NULL,
    ai_response NVARCHAR(MAX) NOT NULL
);