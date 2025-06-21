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
    Devuelve (artist_id, status) donde status puede ser: 'existente', 'insertado', 'error'
    """
    if not artist_name:
        return None, 'error'
    
    cursor.execute("SELECT artist_id FROM artists WHERE name = ?", (artist_name,))
    result = cursor.fetchone()
    if result:
        return result[0], 'existente'
    
    try:
        print(f"🎵 Intentando insertar artista: '{artist_name}'")
        cursor.execute("INSERT INTO artists (name) OUTPUT INSERTED.artist_id VALUES (?)", (artist_name,))
        result = cursor.fetchone()
        artist_id = result[0] if result else None
        print(f"✅ Artista insertado con ID: {artist_id}")
        return artist_id, 'insertado'
    except Exception as e:
        print(f"❌ Error al insertar artista '{artist_name}': {e}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        if hasattr(e, 'args') and len(e.args) > 1:
            print(f"❌ Código de error SQL: {e.args[0]}")
            print(f"❌ Mensaje de error SQL: {e.args[1]}")
        return None, 'error'

def cargar_datos_spotify():
    """
    Carga los datos del archivo CSV de Spotify a la base de datos.
    Procesa artistas, tracks y características de audio.
    """
    print("📥 Cargando datos desde el CSV a la base de datos...")
    
    # Contadores para el resumen final
    contadores = {
        'total_filas': 0,
        'artistas_insertados': 0,
        'artistas_existentes': 0,
        'artistas_fallidos': 0,
        'tracks_insertados': 0,
        'tracks_existentes': 0,
        'tracks_fallidos': 0,
        'audio_features_insertados': 0,
        'audio_features_fallidos': 0
    }
    
    # Verificar si el archivo CSV existe
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: No se encontró el archivo {CSV_FILE}")
        return contadores
    
    try:
        df = pd.read_csv(CSV_FILE)
        contadores['total_filas'] = len(df)
        print(f"✅ CSV cargado exitosamente. Filas encontradas: {len(df)}")
        print(f"📊 Columnas disponibles: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error al leer el archivo CSV: {e}")
        return contadores

    conn = None
    cursor = None

    try:
        conn = get_connection()
        if conn is None:
            print("❌ No se pudo establecer conexión con la base de datos.")
            return

        cursor = conn.cursor()

        for _, row in df.iterrows():
            # ...existing code...
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

                artist_id, artist_status = get_or_create_artist(cursor, artist_name)
                  # Actualizar contadores de artistas
                if artist_status == 'insertado':
                    contadores['artistas_insertados'] += 1
                elif artist_status == 'existente':
                    contadores['artistas_existentes'] += 1
                else:  # error
                    contadores['artistas_fallidos'] += 1
                
                if artist_id is None:
                    print(f"⚠️ No se pudo insertar artista, fila omitida. Número de registro: {_}")
                    continue
            except Exception as e:
                print(f"⚠️ Error inesperado al procesar artista. Número de registro: {_}. Error: {e}")
                continue
            
            # Preparar campos para track
            track_id = str(row.get("track_id", "")).strip()
            track_name = str(row.get("track_name", "")).strip()
            album_name = str(row.get("track_album_name", "")).strip()

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
                release_date = None            # Verificar si el track ya existe
            cursor.execute("SELECT COUNT(*) FROM tracks WHERE track_id = ?", (track_id,))
            track_exists = cursor.fetchone()[0] > 0
            if track_exists:
                print(f"⚠️ El track con ID {track_id} ya existe. Número de registro: {_}")
                contadores['tracks_existentes'] += 1
                continue

            # Insertar track
            try:
                cursor.execute("""
                    INSERT INTO tracks (
                        track_id, name, artist_id, album_name, release_date,
                        duration_ms, key_signature, mode, popularity, genres
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)                """, (
                    track_id, track_name, artist_id, album_name, release_date,
                    row.get("duration_ms"), row.get("key", 0), row.get("mode", 0),
                    row.get("track_popularity", 0), row.get("playlist_genre", "")
                ))
                contadores['tracks_insertados'] += 1
            except Exception as e:
                print(f"❌ Error al insertar track {track_id}. Número de registro: {_}. Error: {e}")
                contadores['tracks_fallidos'] += 1
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
                contadores['audio_features_insertados'] += 1
            except Exception as e:
                print(f"⚠️ Error al insertar características para {track_id}. Número de registro: {_}. Error: {e}")
                contadores['audio_features_fallidos'] += 1
                continue

            conn.commit()

        # Mostrar resumen final
        print("\n" + "="*60)
        print("📋 RESUMEN DE CARGA DE DATOS DE SPOTIFY")
        print("="*60)
        print(f"📊 Total de filas procesadas: {contadores['total_filas']}")
        print(f"")
        print(f"🎵 ARTISTAS:")
        print(f"   ✅ Insertados nuevos: {contadores['artistas_insertados']}")
        print(f"   📝 Ya existían: {contadores['artistas_existentes']}")
        print(f"   ❌ Fallidos: {contadores['artistas_fallidos']}")
        print(f"")
        print(f"🎵 TRACKS:")
        print(f"   ✅ Insertados nuevos: {contadores['tracks_insertados']}")
        print(f"   📝 Ya existían: {contadores['tracks_existentes']}")
        print(f"   ❌ Fallidos: {contadores['tracks_fallidos']}")
        print(f"")
        print(f"🎵 CARACTERÍSTICAS DE AUDIO:")
        print(f"   ✅ Insertadas: {contadores['audio_features_insertados']}")
        print(f"   ❌ Fallidas: {contadores['audio_features_fallidos']}")
        print(f"")
        
        # Calcular totales exitosos
        total_exitosos = (contadores['artistas_insertados'] + 
                         contadores['tracks_insertados'] + 
                         contadores['audio_features_insertados'])
        total_fallidos = (contadores['artistas_fallidos'] + 
                         contadores['tracks_fallidos'] + 
                         contadores['audio_features_fallidos'])
        
        print(f"🔍 RESUMEN GENERAL:")
        print(f"   ✅ Total de operaciones exitosas: {total_exitosos}")
        print(f"   ❌ Total de operaciones fallidas: {total_fallidos}")
        print(f"   📊 Tasa de éxito: {(total_exitosos/(total_exitosos+total_fallidos)*100):.1f}%" if (total_exitosos+total_fallidos) > 0 else "   📊 Tasa de éxito: N/A")
        print("="*60)
        print("✅ Proceso de carga completado.")

    except Exception as e:
        print("❌ Error general al cargar datos:", e)
        return contadores

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return contadores


# Mantener compatibilidad hacia atrás
def main():
    """Función main para compatibilidad. Usa cargar_datos_spotify()."""
    cargar_datos_spotify()