# Introduction



## Project Structure

- We have mainly four sessions:

  - `Ollama`

    - The local LLM server for the game. It is used to generate the story, handle player input etc.

  - `Game` (located in `game`)

    - Handle the game logic and communication with `Ollama`.

  - `Backend` (located in `backend`)

    - Handle the communication between the `Game` and `Frontend`.

  - `Frontend` (located in `frontend`)
    - Handle the frontend logic and communication with `Backend`.

# How to run the game

## Installation

1. Run `docker-compose up --build` to build everything and start container

2. Run `docker-compose exec -it ollama ollama run llama3.1:8b` to download `llama3.1:8b` as the LLM.

   - After you see the "success" message (you can try to type something and interact to the LLM), you can just type `/bye` to the console to exit.

3. Run `docker-compose exec -it backend /bin/sh` to enter the backend container.

   - Then `cd backend` and run `python manage.py makemigrations` and `python manage.py migrate` to generate the database
   - At the end, just type `exit` to exit the container.

4. Now run `docker-compose restart` to reload the container.

5. Open `http://localhost:5173` in your browser to start the game.

## Start the game

I strongly suggest you just to play around with the web instead of watching this session. I hope I make the website "straight-forward" enough for you to understand how the game works.

## Close the server

- We can simply close the server by closing the container. 
