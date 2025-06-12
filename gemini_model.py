from dotenv import load_dotenv
from config.settings import GEMINI_API_KEY
from prompts.prompts import PROMPT_ANALISIS_MUSICAL
from google import genai
from google.genai import types
import anthropic
import os
import json # Add this import

load_dotenv()

def load_prompt() -> str:
    return PROMPT_ANALISIS_MUSICAL

def generate_prompt(user_input: str) -> str:
    """
    Genera el prompt para enviar al modelo Gemini basado en la entrada del usuario.
    """
    return f"{load_prompt()}\n{user_input}"

def call_gemini(user_input: str) -> str:
    """
    Realiza la llamada al modelo Gemini utilizando la biblioteca google-genai.
    """
    print("Llamando al modelo: Gemini")

    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    model = "gemini-2.0-flash"
    # Usar generate_prompt para incluir el system prompt
    prompt_text = generate_prompt(user_input)
    contents = [
        types.Content(
            role="user", # El rol sigue siendo "user" pero el texto contiene el system prompt + user input
            parts=[
                types.Part.from_text(text=prompt_text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text

    return response_text

def generar_consulta_sql(modelo: str, pregunta: str, estructura_tabla: str, prompt_base: str) -> str:
    """
    Genera una consulta SQL utilizando el modelo especificado.
    
    Args:
        modelo (str): Nombre del modelo a utilizar (Gemini o Anthropic).
        pregunta (str): Pregunta en lenguaje natural.
        estructura_tabla (str): Estructura de la tabla en formato SQL.
        prompt_base (str): Prompt base definido en prompts.py.

    Returns:
        str: Consulta SQL generada.
    """
    # Combinar el prompt base con la estructura de la tabla y la pregunta
    prompt = prompt_base.format(ESTRUCTURA_TABLA=estructura_tabla, pregunta=pregunta)

    if modelo.lower() == "gemini":
        client = genai.Client(api_key=GEMINI_API_KEY)
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(response_mime_type="text/plain")

        response_text = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text

        return response_text.strip()

    elif modelo.lower() == "anthropic":
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return message.content[0].text.strip()

    else:
        raise ValueError("Modelo no soportado: Debe ser 'gemini' o 'anthropic'")


def generate_response_from_data(user_question: str, db_data: list, table_schema_prompt: str) -> str:
    """
    Generates a natural language response from database data using Gemini.
    """
    print("Llamando al modelo Gemini para generar respuesta desde datos...")

    client = genai.Client(api_key=GEMINI_API_KEY)
    # Using a specific version like "gemini-1.5-flash-001" or "gemini-1.5-flash-latest"
    # "gemini-1.5-flash-latest" is good for always using the most up-to-date flash model.
    model_name = "gemini-1.5-flash-latest"

    data_string = ""
    if not db_data:
        # This string will inform the LLM about the empty data.
        data_string = "No relevant data was found in the database to answer the user's question."
    else:
        # Convert list of dicts to a JSON string for cleaner and more structured prompt input
        data_string = json.dumps(db_data, indent=2, ensure_ascii=False)

    # Construct the prompt
    prompt = f"""
{table_schema_prompt}

Here is the data retrieved from the database based on a query derived from the user's question:
<DATABASE_RESULTS>
{data_string}
</DATABASE_RESULTS>

User's original question: "{user_question}"

Based *only* on the information within the <DATABASE_RESULTS> tags provided above and the table structures defined in the initial prompt section, formulate a natural language answer to the "User's original question".
- Do not refer to SQL queries, the process of querying the database, or the term "database" itself if possible. Act as if you are an expert directly analyzing the provided data.
- If the <DATABASE_RESULTS> are empty (indicated by the "No relevant data..." message) or do not contain sufficient information to answer the question, state that you cannot answer the question with the provided information or that no relevant information was found.
- Be concise and directly answer the question.
- Do not invent or infer information not explicitly present in the <DATABASE_RESULTS>.
"""

    contents = [
        types.Content(
            role="user", # Role is user as we are providing all context in one go
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    try:
        response = client.generate_content(
            model=model_name,
            contents=contents,
            generation_config=generate_content_config,
        )

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text.strip()
        elif hasattr(response, 'text'): # Fallback for simpler response structures if API changes
             return response.text.strip()
        else:
            print(f"❌ Error: Could not extract text from Gemini response. Response: {response}")
            return "Error: Unable to extract a valid response from the AI model."

    except Exception as e:
        print(f"❌ Error calling Gemini API in generate_response_from_data: {e}")
        return f"Error: Could not generate a response due to an API error: {str(e)}"
