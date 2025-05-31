from llama_cpp import Llama
from ..Const import MODEL_PATH


class LLMModel:
    def __init__(self):
        self.setup_llm(MODEL_PATH)

    def setup_llm(self, model_path: str):
        print(f"Loading model: {model_path}")

        self.llm = Llama(
            model_path=model_path,
            n_ctx=8192,  # Use 8K context
            n_threads=8,  # Adjust based on your CPU cores
            n_gpu_layers=0,  # Set to 0 for CPU, or a higher number for GPU offloading
            verbose=False,
        )

        print("Model loaded successfully")

    def get_model(self):
        return self.llm
