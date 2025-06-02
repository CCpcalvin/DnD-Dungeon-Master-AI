import sys

sys.path.append("..")

from game.models.LLMProvider import Local_LLAMAProvider, OpenRouterProvider

def test_open_router():
    client = OpenRouterProvider()

    completion = client.get_completion(
        messages=[
            {
                "role": "user",
                "content": "What is the meaning of life?. I want 10-20 words of answer.",
            }
        ],
        max_tokens=100,
    )

    print(completion)


def test_llama():
    client = Local_LLAMAProvider()

    completion = client.get_completion(
        messages=[
            {
                "role": "user",
                "content": "What is the meaning of life?. I want 10-20 words of answer.",
            }
        ],
        max_tokens=100,
    )

    print(completion)


test_open_router()
# test_llama()
