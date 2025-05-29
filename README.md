# Introduction
---



# Installation
--- 
- Firstly we build the docker image. If you simply build it using cpu, then just do 
  ```bash
  # Build CPU image
  docker build -f docker/Dockerfile.cpu -t dnd-master-cpu .

  # Build GPU image
  docker build -f docker/Dockerfile.gpu -t dnd-master-gpu .
  ```

- If you decide to use GPU, you have to install cuda first. 
  - Edit the docker/Dockerfile.gpu for your cuda version. 



- Mainly download the from `requirements.txt`
- For the llama-cpp-python, firstly it is required 
- 
- we can download it using the normal way 
  ```bash
  # Linux and Mac
  CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" \
    pip install llama-cpp-python
  ```

  ```powershell
  # Windows
  CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" \
    pip install llama-cpp-python
  ```
  with GPU support. 
  
  
  See more from https://llama-cpp-python.readthedocs.io/en/latest/



