import requests
from tqdm import tqdm
import os


def download_file(url, filename):
    # Create directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    filepath = os.path.join("models", filename)

    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"Model already exists at {filepath}")
        return filepath

    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))

    with open(filepath, "wb") as f, tqdm(
        desc=filename,
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)

    return filepath


# Download the model
model_url = "https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
model_path = download_file(model_url, "llama-3-8b-instruct.Q4_K_M.gguf")
