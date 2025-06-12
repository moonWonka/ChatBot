import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from db.connection import get_connection
import re

# Cargar variables de entorno
load_dotenv()

CSV_FILE = 'data/spotify.csv'

def get_or_create_artist(cursor, artist_name):
    """
    Busca un artista por nombre. Si no existe, lo inserta.
    Devuelve artist_id.
    """
    if not artist_name:
        return None

    cursor.execute("SELECT artist_id FROM artists WHERE name = ?", (artist_name,))
    result = cursor.fetchone()
    if result:
        return result[0]

    try:
        cursor.execute("INSERT INTO artists (name) VALUES (?)", (artist_name,))
        cursor.execute("SELECT SCOPE_IDENTITY()")
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"⚠️ Error al insertar artista '{artist_name}': {e}")
        return None

def main():
    print("📥 Cargando datos desde el CSV a la base de datos...")
    df = pd.read_csv(CSV_FILE)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        if conn is None:
            print("❌ No se pudo establecer conexión con la base de datos.")
            return

        cursor = conn.cursor()

        for _, row in df.iterrows():
            # Validar artista
            artist_name = row.get("track_artist", "")
            try:
                if isinstance(artist_name, str):
                    artist_name = artist_name
                    if not artist_name:
                        print(f"⚠️ Artista vacío. Se asignará 'Desconocido'. Número de registro: {_}")
                        artist_name = "Desconocido"
                else:
                    print(f"⚠️ Tipo de dato inválido en artista. Se asignará 'Desconocido'. Número de registro: {_}")
                    artist_name = "Desconocido"

                artist_id = get_or_create_artist(cursor, artist_name)
                if artist_id is None:
                    print(f"⚠️ No se pudo insertar artista, fila omitida. Número de registro: {_}")
                    continue
            except Exception as e:
                print(f"⚠️ Error inesperado al procesar artista. Número de registro: {_}. Error: {e}")
                continue

            # Preparar campos para track
            track_id = row.get("track_id", "").strip()
            track_name = row.get("track_name", "").strip()
            album_name = row.get("track_album_name", "").strip()

            try:
                release_date_str = str(row.get("track_album_release_date", ""))
                if len(release_date_str) == 4:  # Caso de año solamente
                    release_date = datetime.strptime(release_date_str, "%Y").date()
                elif len(release_date_str) == 7:  # Caso de año y mes
                    release_date = datetime.strptime(release_date_str, "%Y-%m").date()
                elif len(release_date_str) == 10:  # Caso completo
                    release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
                else:
                    raise ValueError("Formato de fecha no soportado")
            except Exception as e:
                print(f"⚠️ Error al procesar fecha de lanzamiento para el número de registro: {_}. Error: {e}")
                release_date = None

            # Verificar si el track ya existe
            cursor.execute("SELECT COUNT(*) FROM tracks WHERE track_id = ?", (track_id,))
            track_exists = cursor.fetchone()[0] > 0
            if track_exists:
                print(f"⚠️ El track con ID {track_id} ya existe. Número de registro: {_}")
                continue

            # Insertar track
            try:
                cursor.execute("""
                    INSERT INTO tracks (
                        track_id, name, artist_id, album_name, release_date,
                        duration_ms, key_signature, mode, popularity, genres
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    track_id, track_name, artist_id, album_name, release_date,
                    row.get("duration_ms"), row.get("key", 0), row.get("mode", 0),
                    row.get("track_popularity", 0), row.get("playlist_genre", "")
                ))
            except Exception as e:
                print(f"❌ Error al insertar track {track_id}. Número de registro: {_}. Error: {e}")
                continue

            # Insertar audio_features
            try:
                cursor.execute("""
                    INSERT INTO audio_features (
                        track_id, energy, tempo, danceability, loudness,
                        liveness, valence, speechiness, instrumentalness, acousticness
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    track_id, row["energy"], row["tempo"], row["danceability"], row["loudness"],
                    row["liveness"], row["valence"], row["speechiness"],
                    row["instrumentalness"], row["acousticness"]
                ))
            except Exception as e:
                print(f"⚠️ Error al insertar características para {track_id}. Número de registro: {_}. Error: {e}")
                continue

            conn.commit()

        print("✅ Todos los datos fueron cargados correctamente.")

    except Exception as e:
        print("❌ Error general al cargar datos:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()