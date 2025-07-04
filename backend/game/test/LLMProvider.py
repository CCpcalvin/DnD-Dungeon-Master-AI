import sys

sys.path.append("..")

from typing import Literal

from pydantic import BaseModel, Field

from game.models.LLMProvider import *

# Import the IPython module
try:
    from IPython import get_ipython

    ipython = get_ipython()
    if ipython is not None:
        # Get the model from IPython's user namespace
        local_llm = ipython.user_ns.get("local_llm")
        if local_llm is None:
            raise ValueError("No 'local_llm' variable found in IPython namespace")
    else:
        raise ImportError("Not running in IPython")
except (ImportError, ValueError) as e:
    print(f"Warning: {e}. Creating a new model instance.")
    from game.models.LLMProvider import init_llama

    local_llm = init_llama()


class People(BaseModel):
    name: str = Field(..., description="The name of the person.")
    age: int = Field(..., description="The age of the person.")
    gender: Literal["male", "female"] = Field(
        ..., description="The gender of the person."
    )


def test_local_llama():
    model = ollama(local_llm)

    completion = model.get_completion(
        ResponseModel=People,
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
        ResponseModel=People, messages=messages, max_tokens=100, temperature=0.8
    )
    print(completion)


def test_open_router_llama():
    model = Llama_3_3_8B_Instruct()

    completion = model.get_completion(
        ResponseModel=People,
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
