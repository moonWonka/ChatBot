CREATE DATABASE IAPP;

-- Usar la base de datos
USE IAPP;

-- ======================================
-- 🚫 OPCIONAL: Eliminar tablas si ya existen
-- DROP TABLE IF EXISTS audio_features;
-- DROP TABLE IF EXISTS tracks;
-- DROP TABLE IF EXISTS albums;
-- DROP TABLE IF EXISTS artists;
-- ======================================

-- Tabla de artistas
CREATE TABLE artists (
    artist_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Tabla de álbumes
CREATE TABLE albums (
    album_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    release_date DATE
);

-- Tabla de pistas (tracks)
CREATE TABLE tracks (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    artist_id INT NOT NULL,
    album_id VARCHAR(50),
    duration_ms INT,
    key_signature INT,
    mode TINYINT,
    popularity INT,
    genres VARCHAR(MAX), -- 🎵 Campo para etiquetas de géneros separadas por coma
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id),
    FOREIGN KEY (album_id) REFERENCES albums(album_id)
);

-- Tabla de características de audio
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
    FOREIGN KEY (track_id) REFERENCES tracks(id)
);
