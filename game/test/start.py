import sys
sys.path.append("..")

from game.models.LLMProvider import Llama_3_3_8B_Instruct
from game.DungeonMaster import DungeonMaster


if __name__ == "__main__":
    dm = DungeonMaster(provider=Llama_3_3_8B_Instruct())
    dm.start_game()
