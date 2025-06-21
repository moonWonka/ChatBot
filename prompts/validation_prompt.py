# ----------- PROMPT PARA VALIDAR PREGUNTAS -----------

PROMPT_VALIDAR_PREGUNTA = """
Analiza la siguiente pregunta del usuario y determina si es válida para generar una consulta SQL sobre una base de datos de música con las siguientes tablas:

TABLAS DISPONIBLES:
- artists: contiene información de artistas (id, nombre)
- tracks: contiene información de canciones (id, nombre, artista, álbum, fecha de lanzamiento, duración, clave musical, modo, popularidad, géneros)
- audio_features: contiene características de audio de las canciones (energía, tempo, bailable, volumen, en vivo, valencia, discurso, instrumental, acústico)

PREGUNTA DEL USUARIO: "{pregunta}"

INSTRUCCIONES:
1. Si la pregunta está relacionada con música, artistas, canciones, álbumes o características de audio, responde: "VALIDA"
2. Si la pregunta es clara y específica, responde: "VALIDA"
3. Si la pregunta es ambigua y requiere aclaración, responde: "ACLARAR: [explicación de qué necesita aclarar]"
4. Si la pregunta está completamente fuera del contexto musical, responde: "FUERA_CONTEXTO"
5. Si la pregunta contiene términos técnicos de base de datos o menciona tablas/columnas, responde: "FUERA_CONTEXTO"

EJEMPLOS:
- "¿Cuáles son las canciones más populares?" → VALIDA
- "Busca canciones de rock" → VALIDA
- "¿Qué tiempo hace hoy?" → FUERA_CONTEXTO
- "Muéstrame la tabla artists" → FUERA_CONTEXTO
- "Canciones de" → ACLARAR: Necesitas especificar de qué artista, género o características buscas las canciones

Responde únicamente con una de las opciones: VALIDA, ACLARAR: [explicación], o FUERA_CONTEXTO
"""
