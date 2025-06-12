# ----------- ANALÍTICA CON IA (TEXT PROMPTS) -----------

# Opción 1: Análisis de Tendencias Musicales
PROMPT_ANALISIS_MUSICAL = """
Eres un experto analista de tendencias musicales. Tu tarea es analizar la información proporcionada sobre una canción o artista y responder siguiendo estrictamente la siguiente estructura:

**Título del Análisis Musical:**
[Un título creativo y descriptivo del análisis musical]

**Análisis Detallado de la Música:**
[Aquí va tu análisis completo sobre la canción/artista. Considera elementos como género, instrumentación, popularidad, sentimiento general, etc. Sé claro y conciso.]

**Posibles Audiencias Clave:**
[Enumera 2-3 tipos de audiencias que podrían disfrutar de esta música.]

Por favor, analiza la siguiente información:
Nombre de la Canción/Artista: {nombre_cancion_artista}
Género Principal: {genero_principal}
Sentimiento General Percibido: {sentimiento_general}
Nivel de Popularidad (1-10): {popularidad}
Instrumentos Destacados: {instrumentos_destacados}
"""
