import sys

sys.path.append("..")

from game.models.LLMProvider import *

from pydantic import BaseModel, Field


class People(BaseModel):
    name: str = Field(..., description="The name of the person.")
    age: int = Field(..., description="The age of the person.")
    gender: str = Field(..., description="The gender of the person.")


def test_local_llama():
    model = Local_LLAMAProvider()

    completion = model.get_completion(
        response_model=People,
        messages=[
            {
                "role": "user",
                "content": """Generate a random `People` object. Response in JSON format: 
                {
                    "name": "John Doe", # Name ot the person
                    "age": 30, # Age of the person
                    "gender": "male" # Gender of the person
                }""",
            }
        ],
        max_tokens=100,
        temperature=0.8,
    )
    print(completion)


def test_open_router_mistral():
    model = MistralAIProvider()
    messages = [
        {
            "role": "user",
            "content": """
                Generate a random `People` object. Response in JSON format: 
                {
                    "name": "John Doe", # Name ot the person
                    "age": 30, # Age of the person
                    "gender": "male" # Gender of the person
                }
                """,
        }
    ]

    completion = model.get_completion(
        response_model=People, messages=messages, max_tokens=100, temperature=0.8
    )
    print(completion)


def test_open_router_llama():
    model = Llama_3_3_8B_Instruct()

    completion = model.get_completion(
        response_model=People,
        messages=[
            {
                "role": "user",
                "content": "Generate a random `People` object.",
            }
        ],
        max_tokens=100,
        temperature=0.8,
    )
    print(completion)


test_local_llama()
# test_open_router_mistral()
# test_open_router_llama()
