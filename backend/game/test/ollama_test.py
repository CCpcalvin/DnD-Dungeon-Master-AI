from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal

def test_simple_prompt():
    client = OpenAI(base_url="http://ollama:11434/v1", api_key="ollama")

    response = client.chat.completions.create(
        model="llama3.1:8B",
        messages=[
            {
                "role": "user",
                "content": "Why is the sky blue? Give me a 1-2 sentence answer.",
            }
        ],
        temperature=0.8,
    )
    print(response)


class People(BaseModel):
    name: str = Field(..., description="The name of the person.")
    age: int = Field(..., description="The age of the person.")
    gender: Literal["male", "female"] = Field(
        ..., description="The gender of the person.")


def test_structure_prompt():
    client = OpenAI(base_url="http://ollama:11434/v1", api_key="ollama")

    response = client.beta.chat.completions.parse(
        model="llama3.1:8B",
        messages=[
            {
                "role": "user",
                "content": "Generate a random `People` object.",
            }
        ],
        response_format=People,
        temperature=0.8,
    )
    print(response)


if __name__ == "__main__":
    # test_simple_prompt()
    test_structure_prompt()
