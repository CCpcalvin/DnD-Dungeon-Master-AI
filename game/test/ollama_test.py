# import ollama
from openai import OpenAI


def main():
    # response = ollama.chat(
    #     model="llama3.2",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": "Why is the sky blue? Give me a 1-2 sentence answer.",
    #         }
    #     ],
    # )
    # print(response)

    client = OpenAI(base_url="http://ollama:11434/v1", api_key="ollama")

    response = client.chat.completions.create(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": "Why is the sky blue? Give me a 1-2 sentence answer.",
            }
        ],
    )
    print(response)

    # response = OpenAI().post(
    #     "http://ollama:11434/api/chat",
    #     json={
    #         "model": "llama3",
    #         "messages": [
    #             {
    #                 "role": "user",
    #                 "content": "Why is the sky blue? Give me a 1-2 sentence answer.",
    #                 "stream": False,
    #             }
    #         ],
    #     },
    # )
    # response = requests.get("http://ollama:11434")
    # print(response.json())


if __name__ == "__main__":
    main()
