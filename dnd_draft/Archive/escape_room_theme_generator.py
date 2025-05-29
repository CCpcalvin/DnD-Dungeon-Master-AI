from dataclasses import dataclass, asdict
import json
from typing import List, Dict

from LLMModel import LLMModel

@dataclass
class GameTheme:
    title: str
    setting: str
    backstory: str
    atmosphere: str
    visual_style: str
    common_elements: List[str]
    potential_encounters: List[Dict]
    potential_puzzles: List[Dict]

    def save_theme_to_file(self, filename: str = "game_theme.json"):
        """Save the generated theme to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(asdict(self), f, indent=4)

class ThemeGenerator:
    def __init__(self, llm: LLMModel):
        self.llm = llm.get_model()
        with open("theme_prompt.txt", "r") as f:
            self.theme_prompt = f.read()
    
    def generate_theme(self):
        """Generate a complete game theme using the LLM."""
        try:
            # Get the raw JSON response from the LLM
            response = self.llm.create_chat_completion(
                messages=[{"role": "system", "content": self.theme_prompt}],
                response_format={"type": "json_object"},
                temperature=0.9,  # Higher temperature for more creative output
                max_tokens=1500
            )
            
            # Parse the JSON response
            theme_data = json.loads(response["choices"][0]["message"]["content"])
            
            # Convert to GameTheme object
            return GameTheme(
                title=theme_data.get("title", "The Nameless Horror"),
                setting=theme_data.get("setting", ""),
                backstory=theme_data.get("backstory", ""),
                atmosphere=theme_data.get("atmosphere", ""),
                visual_style=theme_data.get("visual_style", ""),
                common_elements=theme_data.get("common_elements", []),
                potential_encounters=theme_data.get("potential_encounters", []),
                potential_puzzles=theme_data.get("potential_puzzles", [])
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error generating theme: {e}")
            # Return a default theme if generation fails
            return self._get_default_theme()
