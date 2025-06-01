from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
client = OpenAI()

class SQLResponse(BaseModel):
    sql_query: str
    explanation: str
    tables_used: list[str]

def load_prompt() -> str:
    with open("prompts/base_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()

def generate_sql_query(user_question: str) -> SQLResponse:
    system_prompt = load_prompt()

    response = client.responses.parse(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        text_format=SQLResponse
    )

    return response.output_parsed
