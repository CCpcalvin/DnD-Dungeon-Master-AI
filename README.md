# Table of Contents

- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [For CS50W Grading](#for-cs50w-grading)
  - [Distinctiveness and Complexity](#distinctiveness-and-complexity)
    - [Distinctiveness](#distinctiveness)
    - [Complexity](#complexity)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Using Docker Compose](#using-docker-compose)
    - [For Window](#for-window)
    - [For Mac](#for-mac)
  - [Close the server](#close-the-server)
- [Game](#game)
  - [Start the game](#start-the-game)
  - [How to play the game](#how-to-play-the-game)
  - [Game mechanics and common terminologies](#game-mechanics-and-common-terminologies)

# Introduction

Hi! This is my final project for "CS50's Web Programming with Python and JavaScript". It took me a significant amount of time to complete this project, and I hope you enjoy it.

I developed this project because I was inspired by _Baldur's Gate 3_ (BG3), which I've been thoroughly enjoying. One of BG3's greatest strengths is its freedom—players can do almost anything they want, and the game dynamically adapts to their actions. While BG3 doesn't offer truly infinite choices (as you're still limited to pre-programmed options), it provides an impressive amount of flexibility. This led me to wonder: what if we could create a game with infinite choices, where the game could adapt to any player's action? This project tries to explore the concept of using AI to respond to player actions while maintaining game rules and narrative coherence. My original vision was to create an AI that functions like a Game Master (GM) in a tabletop role-playing game. The concept involves providing the AI with complete story and puzzle details, allowing it to guide players through the world. The AI would then evaluate player actions through dice rolls and determine appropriate consequences—essentially serving as a GM.

I initially underestimated the complexity of this project. To make it suitable as a capstone project, I had to scale back many features. Nevertheless, creating a DnD-style web game required me to learn numerous technologies beyond the course curriculum, including implementing responsive UIs with `React Native`, integrating `Ollama` and `OpenAI` for local LLM communication, and mastering effective LLM prompting techniques.

# For CS50W Grading

## Distinctiveness and Complexity

### Distinctiveness

This project stands out from others in the course as a web-based game application featuring a responsive UI. It clearly differs from:

- a search page
- wiki application
- an e-commerce website
- a mail application or a social network application

### Complexity

This project consists of several key components:

- `Ollama`

  - The local LLM server for the game. It is used to generate the story, handle player input etc.

- `Game` (located in `game`)

  - Handle the game logic and communication with `Ollama`.

- `Backend` (located in `backend`)

  - Handle the communication between the `Game` and `Frontend`.

- `Frontend` (located in `frontend`)
  - Handle the frontend logic and communication with `Backend`.

If we only focus on the web development parts i.e. `Backend` and `Frontend`, we already have

- `Backend`

  - I have used several `Model`, such as `GameSession`, `GameEvent`, `PlayerInfo`, etc to store the game state, player info, floor history etc, such that we can load the entire game state from the database.
  - Make use of `Django REST framework` to handle API calls
  - Make use of `JWT` to handle user authentication, since we are using `React Native` as the frontend

- `Frontend`
  - This session entirely is already beyond this course (maybe it is kind of relevant to the `React` session in lecture 6)
  - Obviously `JavaScript` is used to handle the frontend logic. For example, I use `JavaScript` to handle `JWT` authentication
  - Responsive UI with `Tailwind CSS`
  - We have `SidePanel` that can slide in and out; we have `TypeAnimation` to simulate typing effect and much more
  - The container and the text will be collapsed if the viewport is too narrow, so it is mobile-responsive.

I strongly believe that this project is complex enough for a capstone project.

# Installation

## Prerequisites

- `Docker` and `Docker Compose`
- For Window: install `cuda` for `Ollama` to speed up the LLM performance using GPU.

- For Mac: install `Ollama` manually
  - It is because `Docker` does not support GPU ;(.

## Using Docker Compose

### For Window

Everything is packed in the `Docker`.

1. Open a terminal and run `docker-compose build` to build the images.

2. Then run `docker-compose up` to start the containers.

3. Open a new terminal and run `docker-compose exec -it ollama ollama run llama3.1:8b` to download `llama3.1:8b` as the LLM.

   - After you see the "success" message (you can try to type something and interact with the LLM), you can just type `/bye` to the console to exit.

4. Open `http://localhost:5173` in your browser to start the game.

### For Mac

1. Open a terminal and run `docker-compose build frontend backend` to build the images for `Frontend` and `Backend` only

2. Download `llama3.1:8b` from `Ollama` and run it in the background.

   - Check out the [Ollama](https://ollama.com/) website for more information.

   - Typically once the `Ollama` is running, you can just type `ollama run llama3.1:8b` to download `llama3.1:8b` as the LLM.

3. Configure the environment variable `OLLAMA_URL`

   - You can use `.env` file to set the environment variable `OLLAMA_URL`.

     - You can follow the `.env.example` to create the `.env` file.

   - If you just run `Ollama` locally without any configuration, then you can set `OLLAMA_URL` to `http//host.docker.internal:11434/v1`.

   - If you want to change the port for `Ollama`, you can set the environment variable `OLLAMA_HOST`

     - You can simply run `OLLAMA_HOST=0.0.0.0:11435 ollama serve` to run `Ollama` with the port `11435`.

4. Then run `docker-compose up frontend backend` to start the containers.

5. Open `http://localhost:5173` in your browser to start the game.

## Close the server

- We can simply close the server by closing the container.

# Game

I recommend exploring the web interface directly, as I've designed it to be intuitive. The following sections explain the game mechanics in detail if you need guidance.

## Start the game

To begin a new game, follow these steps:

1. Register an account. You can go to the `Register` page by clicking the `Login / Register` button in the `Home` page, then click `Register here` in the login page.
2. After logging in / registration, you can create a new session by clicking the "New Adventure" button on the `Home` page.
3. Now you enter `PlayerCreation` page, you can just enter your name, and distribute your stats. The stats will affect how successful you do for certain actions. For example, if your intelligence is high, you are more likely to decrypt the secret message.
4. After you finish the player creation, you can click `Begin Your Adventure` to start the game.

## How to play the game

The game is straightforward to play. The AI generates an evolving story, and your role is to respond with actions that shape the narrative. Interact with the `PlayerInput` section at the bottom of the screen using either of these methods:

1. One is `What do you want to do`. In this case, you just need to type your action and submit it. The AI will judge how well you do the action and the consequences of your action.

   - There are also some suggested actions that you can click, and the action will automatically populate your input region.

2. One is `Continue`. This is just for a break of a game. Once you press continue, then the story continues.

The left arrow button on the side toggles the left panel, where you can view the game theme, current floor, and your character's details. Understanding your character's strengths will help you make optimal decisions throughout the game.

## Game mechanics and common terminologies

- `DC`: For each player action, the AI will determine the **Difficulty Class** (DC) of the action. The DC is a number that represents the difficulty of the action. The higher the DC, the more difficult the action is.

  - The player will roll a 1d10 (1 dice with 10 faces), plus the relevant attribute modifier of the action to see the result of the action. If the final number is higher than the DC, it means the action is successful, otherwise, it is a failure.
  - There are some exceptions. If you roll a 1, the action must be a critical fail, and it comes with a greater penalty. On the other hand, if you roll a 10, the action must be a critical success, and it comes with a greater reward.
  - We can see the system calculation during the game (the message starts with `System`).

- Common short forms of the attributes:
  - `STR`: Strength
  - `DEX`: Dexterity
  - `CON`: Constitution
  - `INT`: Intelligence
  - `WIS`: Wisdom
  - `CHA`: Charisma
