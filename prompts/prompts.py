# ----------- ANALÍTICA CON IA (TEXT PROMPTS) -----------

# Opción 1: Análisis de Tendencias
PROMPT_TENDENCIAS_SENTIMIENTO = """
Analiza el siguiente conjunto de datos agregados extraídos de un análisis automatizado de noticias mediante inteligencia artificial.

Frecuencia de sentimientos detectados:
- Positivo: {positivo}
- Negativo: {negativo}
- Neutro: {neutro}
- Neutral: {neutral}

Distribución de nivel de riesgo:
- Bajo: {riesgo_bajo}
- Medio: {riesgo_medio}
- Alto: {riesgo_alto}

Frecuencia de indicador de violencia:
- Sí: {violencia_si}
- No: {violencia_no}
"""
