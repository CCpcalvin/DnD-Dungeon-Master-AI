import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from game.DungeonMaster import DungeonMaster
from game.models.LLMProvider import ollama

dm = DungeonMaster(provider=ollama())

dm.init_game(mock=1)
dm.non_combat_floor.init_floor(mock=1)
