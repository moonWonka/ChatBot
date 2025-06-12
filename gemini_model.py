from dotenv import load_dotenv
from config.settings import GEMINI_API_KEY
from prompts.prompts import PROMPT_ANALISIS_MUSICAL
from google import genai
from google.genai import types
import anthropic
import os

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
