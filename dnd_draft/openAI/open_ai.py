import os
import time
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()


class RateLimiter:
    def __init__(self, calls_per_minute):
        self.calls_per_minute = calls_per_minute
        self.last_call_time = 0
        self.min_interval = 60.0 / calls_per_minute

    def wait_if_needed(self):
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time

        if time_since_last_call < self.min_interval:
            sleep_time = self.min_interval - time_since_last_call
            time.sleep(sleep_time)

        self.last_call_time = time.time()


class DnDDM:
    def __init__(self):
        self.model = os.getenv("MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.rate_limiter = RateLimiter(
            calls_per_minute=int(os.getenv("RATE_LIMIT", 3))
        )
        self.encoding = tiktoken.encoding_for_model(self.model)
        self.daily_token_count = 0
        self.max_daily_tokens = int(os.getenv("MAX_TOKENS_PER_DAY", 40000))

    def estimate_tokens(self, messages):
        """Approximate token count using tiktoken"""

        tokens_per_message = 3  # Adjust based on your message format
        tokens_per_name = 1  # If you use the 'name' field

        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(self.encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name

        num_tokens += 3  # Every reply is primed with assistant
        return num_tokens

    def check_token_limit(self, prompt_tokens, response_tokens=0):
        total = prompt_tokens + response_tokens

        if self.daily_token_count + total > self.max_daily_tokens:
            remaining = self.max_daily_tokens - self.daily_token_count
            raise Exception(f"Daily token limit reached. {remaining} tokens remaining.")

        self.daily_token_count += total
        return True

    # @retry(
    #     stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    # )
    def get_dm_response(self, prompt, temperature=0.7, max_tokens=200):
        # Check rate limit
        self.rate_limiter.wait_if_needed()

        # Count tokens in prompt
        prompt_tokens = self.estimate_tokens(prompt)
        self.check_token_limit(prompt_tokens, max_tokens)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative Dungeon Master for a D&D game.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Update token count with actual usage
            # completion_tokens = response.usage.completion_tokens
            # self.daily_token_count += completion_tokens

            # usage = response.usage
            # print(f"Prompt tokens: {usage.prompt_tokens}")
            # print(f"Completion tokens: {usage.completion_tokens}")
            # print(f"Total tokens: {usage.total_tokens}")

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise


# Example usage
if __name__ == "__main__":
    dm = DnDDM()
    print(
        dm.estimate_tokens(
            [
                {
                    "role": "system",
                    "content": "You are a creative Dungeon Master for a D&D game.",
                },
                {
                    "role": "user",
                    "content": "Describe a dark forest the players have entered.",
                },
            ]
        )
    )

    # def example_usage():
    #     prompt = "Describe a dark forest the players have entered."
    #     try:
    #         response = dm.get_dm_response(prompt, max_tokens=100)
    #         print("DM:", response)
    #         print(f"Tokens used today: {dm.daily_token_count}/{dm.max_daily_tokens}")

    #     except Exception as e:
    #         print(f"Error: {e}")

    # example_usage()
    # 943
    # 409
