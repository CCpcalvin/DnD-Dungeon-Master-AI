import json

# string = '{\n    "respond_message": "You step out of the elevator and onto the first floor of the mysterious tower. The air is stale and musty, and the walls are adorned with cobweb-covered portraits of people you don\'t recognize. The room is dimly lit by flickering torches, casting eerie shadows on the walls. Ahead of you, a grand staircase curves upward, disappearing into the darkness above.",\n    "suggested_actions": [\n        "Investigate the portraits on the wall",\n        "Head up the staircase to explore the tower",\n        "Custom action (type your own)"\n    ],\n    "health_change": 0,\n    "next_floor": false,\n    "inventory_changes": {},\n    "status_effects": [],\n    "game_over": false\n}'

# data = json.loads(string)
# print(data)

# respond_message=data.get("respond_message", "")
# suggested_actions=data.get("suggested_actions", [])
# health_change=data.get("health_change", 0)
# next_floor=data.get("next_floor", False)
# inventory_changes=data.get("inventory_changes", {})
# status_effects=data.get("status_effects", [])
# game_over=data.get("game_over", False)


# print(respond_message)
# print(suggested_actions)
# print(health_change)
# print(next_floor)
# print(inventory_changes)
# print(status_effects)
# print(game_over)

# my_dict = {'Floor 1': 'No history available'}
# print(json.dumps(my_dict))


# my_dict = '{\n    "narrative_consistency": "true",\n    "action_type": "ability_check",\n    "relevant_attribute": "intelligence",\n    "difficulty_class": 6,\n    "success_response": {\n        "message": "You carefully examine the tapestries and notice that one of them seems to be slightly torn. With a bit of effort, you manage to tear it off the wall, revealing a small compartment behind it. Inside, you find a small, intricately carved stone with a faint glow.",\n        "health_change": 0,\n        "inventory_changes": {"glowing_stone": 1},\n    "failure_response": {\n        "message": "You try to examine the tapestries, but they seem to be just decorative. You find nothing of interest.",\n        "health_change": 0,\n        "inventory_changes": {},\n    "luck": 5\n} } }'
# data = json.loads(my_dict)
# # print(data)
# # print(data.get("success_response", "").get("inventory_changes", ""))
# print(data.get("failure_response", "").get("message", ""))
