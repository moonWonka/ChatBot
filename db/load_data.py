import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from db.connection import get_connection

# Cargar variables de entorno
load_dotenv()

# Ruta del archivo CSV
CSV_FILE = 'data/spotify.csv'  # Asegúrate de que este path sea correcto

def get_or_create(cursor, table, column, value, extra_fields=None):
    """
    Busca si existe el valor en una tabla. Si no existe, lo inserta.
    """
    query = f"SELECT {column}_id FROM {table} WHERE {column} = ?"
    cursor.execute(query, (value,))
    result = cursor.fetchone()
    if result:
        return result[0]

    if extra_fields:
        cols = ', '.join([column] + list(extra_fields.keys()))
        placeholders = ', '.join(['?'] * (1 + len(extra_fields)))
        values = [value] + list(extra_fields.values())
    else:
        cols = column
        placeholders = '?'
        values = [value]

    insert_query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
    cursor.execute(insert_query, values)
    return cursor.lastrowid

# Actualizar el código principal para reflejar la estructura de las tablas

def main():
    # Cargar CSV
    df = pd.read_csv(CSV_FILE)

    try:
        conn = get_connection()
        if conn is None:
            print("❌ No se pudo establecer conexión con la base de datos.")
            return

        cursor = conn.cursor()

        for _, row in df.iterrows():
            # Insertar artista
            artist_id = get_or_create(cursor, "artists", "name", row["artist_name"])

            # Insertar álbum
            release_date = row.get("release_date", None)
            try:
                release_date = datetime.strptime(str(release_date), "%Y-%m-%d").date()
            except:
                release_date = None
            album_id = get_or_create(cursor, "albums", "name", row["album_name"], {
                "release_date": release_date
            })

            # Insertar track
            cursor.execute("""
                INSERT INTO tracks (id, name, artist_id, album_id, duration_ms, key_signature, mode, popularity, genres)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["track_id"], row["track_name"], artist_id, album_id, row["duration_ms"],
                row.get("key", 0), row.get("mode", 0), row.get("popularity", 0), row.get("genres", "")
            ))
            track_id = cursor.lastrowid

            # Insertar características de audio
            cursor.execute("""
                INSERT INTO audio_features (track_id, energy, tempo, danceability, loudness,
                liveness, valence, speechiness, instrumentalness, acousticness)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                track_id, row["energy"], row["tempo"], row["danceability"], row["loudness"],
                row["liveness"], row["valence"], row["speechiness"],
                row["instrumentalness"], row["acousticness"]
            ))

            conn.commit()

        print("✅ Datos cargados correctamente.")

    except Exception as e:
        print("❌ Error al conectar o insertar en la base de datos:", e)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    main()
