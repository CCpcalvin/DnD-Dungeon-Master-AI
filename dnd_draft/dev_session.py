import llama, escape_room_theme_generator, Tower

# Initialize the model once
print("Loading LLM (this will take a moment)...")
llm = llama.LLMModel()

def reload_dm():
    """Reload only the DnDDM class while keeping the LLM in memory"""
    from importlib import reload
    reload(llama)  # Reload the module
    return llama.DnDDM(llm)

def reload_theme_generator():
    """Reload only the ThemeGenerator class while keeping the LLM in memory"""
    from importlib import reload
    reload(escape_room_theme_generator)  # Reload the module
    return escape_room_theme_generator.ThemeGenerator(llm)

def reload_towerDM():
    """Reload only the Tower class while keeping the LLM in memory"""
    from importlib import reload
    reload(Tower)  # Reload the module
    return Tower.DungeonMaster(llm)

# Initialize the DM
dm = llama.DnDDM(llm)
print("Ready! Type `dm = reload_dm()` after making changes to DnDDM class.")

# Initialize the ThemeGenerator
generator = escape_room_theme_generator.ThemeGenerator(llm)
print("Ready! Type `generator = reload_theme_generator()` after making changes to ThemeGenerator class.")

# Initialize the Tower
towerDM = Tower.DungeonMaster(llm)
print("Ready! Type `towerDM = reload_towerDM()` after making changes to TowerDungeonMaster class.")
