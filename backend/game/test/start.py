import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game.models.LLMProvider import ollama
from game.DungeonMaster import DungeonMaster


if __name__ == "__main__":
    dm = DungeonMaster(provider=ollama())
    dm.start_game()
