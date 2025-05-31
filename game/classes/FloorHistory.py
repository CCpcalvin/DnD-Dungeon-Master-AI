
class FloorHistory:
    def __init__(self):
        self.content = []
        self.summary = ""

    def add_narrative(self, narrative: str):
        self.content.append({"role": "Narrator", "content": narrative})
    
    def add_system(self, system: str):
        self.content.append({"role": "System", "content": system})

    def add_player_actions(self, actions: str, success: bool):
        self.content.append({"role": "Player", "content": actions, "success": success})

    def has_summary(self):
        return len(self.summary) > 0

    def has_history(self):
        return len(self.content) > 0

    def __str__(self):
        if not self.has_history():
            return f"No history available"
        
        string = ""
        for item in self.content:
            if item["role"] == "Player":
                string += f"Player: {item['content']}.({'Success' if item['success'] else 'Failed'})\n"
            else:
                string += f"{item['role']}: {item['content']}\n"

        return string


    def history_prompt(self):
        if not self.has_history():
            return "No history available"
        
        string = ""
        for item in self.content:
            if item["role"] == "Player":
                string += f"Player: {item['content']}.({'Success' if item['success'] else 'Failed'})\n"
            elif item["role"] == "Narrator":
                string += f"Narrator: {item['content']}\n"

        return string
        
