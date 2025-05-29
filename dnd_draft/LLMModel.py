from llama_cpp import Llama

class LLMModel:
    def __init__(self, model_path=None):
        # Default model path if none provided
        if model_path is None:
            model_path = "../models/llama-3-8b-instruct.Q4_K_M.gguf"

        self.model_path = model_path
        self.setup_llm(model_path)

    def progress_callback_wrapper(self, progress):
        # Convert to percentage (0-100)
        percent = min(int(progress * 100), 100)
        self.pbar.n = percent
        self.pbar.refresh()

    def setup_llm(self, model_path):
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