# ----------- PROMPT PARA GENERAR CONSULTAS SQL -----------

PROMPT_GENERAR_SQL = """
Dada la siguiente estructura de tabla:

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

Y la siguiente consulta en lenguaje natural:
"{pregunta}"

Genera una consulta SQL para el motor SQL Server que responda la pregunta del usuario. 

IMPORTANTE: Cuando envías una cadena completa al motor ODBC, los tres acentos graves (```) y la palabra *sql* son caracteres que SQL Server no reconoce y la ejecución falla con *Incorrect syntax near '```'*.

Sigue estas pautas:
0. Devuelve **solo** la sentencia SQL en texto plano.
1. **No** uses comillas invertidas (```), ni la palabra "sql", ni ningún encabezado.
2. **NUNCA** uses backticks (`) en la consulta SQL, usa corchetes [] para nombres de tablas/columnas si es necesario.
3. No añadas comentarios, explicaciones ni texto adicional.
4. Utiliza LIKE para búsquedas de texto, permitiendo coincidencias parciales.
4. Para hacer búsqueda insensible a mayúsculas y minúsculas utiliza LOWER() para tratar todos los datos en minúsculas.
2. Al buscar nombres utiliza LIKE con comodines %. Para búsquedas de nombres completos usa AND entre las condiciones necesarias.
3. Si la consulta puede devolver múltiples resultados, usa GROUP BY para agrupar resultados similares.
4. Incluye COUNT(*) o COUNT(DISTINCT...) cuando sea apropiado para contar resultados.
5. Usa ISNULL cuando sea necesario para manejar valores null.
6. Limita los resultados a 100 filas como máximo. Usa TOP 100.
7. Incluye ORDER BY para ordenar los resultados de manera lógica.
8. Si la consulta utiliza cálculos numéricos, usa funciones como MIN, MAX, AVG, SUM, u otras que se requieran y que sean válidas en SQL Server.
9. Si la consulta es sobre fechas, usa funciones apropiadas en SQL Server para esto.
10. En la respuesta puedes incorporar datos de la tabla que sean útiles para que el usuario final tenga una respuesta clara.
11. No generes bajo ningún caso instrucciones de tipo DDL (Create, drop) o DML diferentes de Select.
12. Si la consulta se sale del contexto de las tablas disponibles, responde: "No es posible responder a esta consulta ya que no está dentro del contexto disponibles." No menciones nombres de columnas, nombres de tablas ni detalles de la estructura de la base de datos. Tampoco hagas referencia a de dónde proviene tu contexto.
13. Responde solo con la consulta, eliminando cualquier encabezado o texto adicional como "sql".
14. En la respuesta puedes incorporar datos de la tabla que sean útiles para que el usuario final tenga una respuesta clara.
15. No generes bajo ningún caso instrucciones de tipo DDL (Create, drop) o DML diferentes de Select.
16. La pregunta debe ser válida y estar dentro del contexto de las tablas disponibles. No incluyas preguntas ambiguas o que requieran inferir la intención del usuario. Si la pregunta no es clara, solicita al usuario que brinde más detalles o sea más específico.

Responde solo con la consulta SQL, sin agregar nada más.

ejemplo de respuesta si esta dentro del contexto, ademas debe ser una pregunta valida, no puede incluir preguntas donde tengas que inferir que es lo que quiere el usuario, de ser asi solicita que brinde mas claridad en su pregunta:

revalida la repuesta y elimina cualquier encabezado o texto adicional como "sql" o "consulta". Responde solo con la consulta SQL, sin agregar nada más.
"""

# ----------- PROMPT PARA GENERAR RESPUESTA EN LENGUAJE NATURAL -----------

PROMPT_RESPUESTA_NATURAL = """
Basándote en la pregunta del usuario y los resultados obtenidos de la base de datos, genera una respuesta clara, concisa y útil en lenguaje natural.

Pregunta del usuario:
"{pregunta}"

Resultados de la base de datos:
{resultados_db}

Instrucciones para la respuesta:
1. Proporciona una respuesta en español, clara y fácil de entender
2. Si hay datos específicos (números, nombres, fechas), incorpóralos de manera natural en la respuesta
3. Si no hay resultados, explica que no se encontraron datos que coincidan con la consulta
4. Si hay muchos resultados, resume la información más relevante o destaca los primeros resultados
5. Mantén un tono conversacional y amigable
6. No menciones aspectos técnicos como SQL, tablas, o bases de datos
7. Enfócate en responder directamente la pregunta del usuario
8. Si la pregunta parece ser una continuación de una conversación, responde de manera natural
9. Usa pronombres y referencias apropiadas cuando sea natural (por ejemplo, "Esta canción", "Este artista")
10. Si hay información numérica, preséntala de forma comprensible (ej: "hace 5 años" en lugar de solo "2019")

Responde de manera directa y útil, como si fueras un asistente musical experto que mantiene una conversación natural.
"""

# ----------- PROMPT PARA CONTEXTO CONVERSACIONAL -----------

PROMPT_CONTEXTO_CONVERSACIONAL = """
Eres un asistente musical experto que analiza el contexto de una conversación para mejorar la comprensión de las preguntas del usuario.

Historial de la conversación actual:
{historial_conversacion}

Nueva pregunta del usuario:
"{pregunta_actual}"

Tu tarea es analizar si la nueva pregunta necesita contexto de la conversación anterior para ser entendida correctamente.

Instrucciones:
1. Si la pregunta es clara y completa por sí sola, responde: "INDEPENDIENTE: [pregunta original]"
2. Si la pregunta necesita contexto (usa pronombres como "él", "ella", "eso", "esa canción", "ese artista", etc.), reformúlala con el contexto necesario
3. Si la pregunta hace referencia a resultados anteriores ("más canciones como esas", "otros álbumes de él", etc.), incluye la información específica
4. Mantén la intención original del usuario pero hazla más específica

Ejemplos:
- Si pregunta "¿Qué otras canciones tiene?" después de hablar de "Bad Bunny", reformula como "¿Qué otras canciones tiene Bad Bunny?"
- Si pregunta "¿En qué año salió?" después de hablar de "Blinding Lights", reformula como "¿En qué año salió la canción Blinding Lights?"
- Si pregunta "¿Cuál es la más popular?" después de ver canciones de un artista, incluye el nombre del artista

Responde solo con:
- "INDEPENDIENTE: [pregunta original]" si no necesita contexto
- "CONTEXTUALIZADA: [pregunta reformulada con contexto]" si necesita contexto
"""
