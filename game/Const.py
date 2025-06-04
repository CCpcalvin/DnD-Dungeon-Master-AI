import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_PATH = os.path.join(PROJECT_PATH, "game")

PROMPT_PATH = os.path.join(GAME_PATH, "llm_api", "prompt")
SYSTEM_PROMPT_PATH = os.path.join(PROMPT_PATH, "system")
USER_PROMPT_PATH = os.path.join(PROMPT_PATH, "user")
