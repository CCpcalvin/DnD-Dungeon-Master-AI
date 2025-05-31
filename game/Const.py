import os

MODEL_PATH = "../models/llama-3-8b-instruct.Q4_K_M.gguf"
PROMPT_PATH = "llm_api/prompt"
SYSTEM_PROMPT_PATH = os.path.join(PROMPT_PATH, "system")
USER_PROMPT_PATH = os.path.join(PROMPT_PATH, "user")
