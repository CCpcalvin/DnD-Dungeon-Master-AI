# Introduction


# Project Structure
- We have mainly four sessions: 
  - `Ollama`
    - The local LLM server for the game. It is used to generate the story, handle player input etc.

  - `Game` (located in `game`)
    - Handle the game logic and communication with `Ollama`.

  - `Backend` (located in `backend`)
    - Handle the communication between the `Game` and `Frontend`.

  - `Frontend` (located in `frontend`)
    - Handle the frontend logic and communication with `Backend`.
  




# How to run it
## Using Docker

1. Run `docker-compose up --build` to build everything
2. Run `docker-compose exec -it final-ollama-1 ollama run llama3` to download `llama3` as the LLM.
   - We mainly use llama3 for the LLM.

