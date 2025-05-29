from __future__ import annotations
from llama_cpp import Llama
from LLMModel import LLMModel


class DnDDM:
    def __init__(self, model: LLMModel):
        self.llm = model.get_model()

        # Conversation history
        self.conversation_history = []

        # Initialize system prompt. It is from llama_system_prompt.txt
        with open("llama_system_prompt.txt", "r") as f:
            self.system_prompt = f.read()

    def format_messages(self):
        """Format the conversation history for the model"""
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add conversation history
        for msg in self.conversation_history[-6:]:  # Keep last 3 exchanges
            messages.append(msg)

        return messages

    def _get_dm_response(self, user_input, max_tokens=1000):
        try:
            return self._get_dm_response_no_error_guard(user_input, max_tokens)

        except Exception as e:
            print(f"Error generating response: {e}")
            return (
                "I'm having trouble thinking right now. What would you like to do next?"
            )

    def _get_dm_response_no_error_guard(self, user_input, max_tokens=1000):
        # Add user input to history
        self.conversation_history.append({"role": "user", "content": user_input})

        # Format messages for the model
        messages = self.format_messages()

        # Generate response
        response = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.2,
            repeat_penalty=1.1,
        )

        # Extract the response
        print(response)
        dm_response = response["choices"][0]["message"]["content"].strip()

        # Add DM response to history
        self.conversation_history.append({"role": "assistant", "content": dm_response})

        # Keep conversation history manageable
        if len(self.conversation_history) > 10:  # Keep last 5 exchanges
            self.conversation_history = self.conversation_history[-10:]

        return dm_response


def test_local_dm():
    print("Initializing Llama 3 8B... (this may take a moment)")
    llm = LLMModel()
    dm = DnDDM(llm)

    print("\nDungeon Master: Welcome to your adventure! (Type 'quit' to end)")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nDungeon Master: Farewell, adventurer!")
            break

        print("\nDungeon Master is thinking...")
        response = dm._get_dm_response_no_error_guard(user_input)
        print(f"\nDungeon Master: {response}")


if __name__ == "__main__":
    test_local_dm()
