from __future__ import annotations

import json, random

from AIClassifyActionResponse import (
    ClassifyActionNarrativeInconsistency,
    ClassifyActionResponse,
    ClassifyActionSuccess,
)
from AIResponse import AIResponse, AIResponseSuccess
from GameState import FloorHistory, GameState, Player


class DungeonMaster:
    def __init__(self, llm):
        self.llm = llm.get_model()
        self.state = GameState()
        self.state.player = self.create_player()
        print("Player created: ", self.state.player)

        self.setup_prompt_template()

    def create_player(self):
        name = "You"
        return Player.create_with_random_stats(name)

    def setup_prompt_template(self):
        """Set up the initial system prompt for the LLM"""
        with open("prompt/system_ai_respond_prompt.txt", "r") as f:
            self.respond_system_prompt = f.read()

        with open("prompt/user_describe_floor_prompt.txt", "r") as f:
            self.describe_floor_system_prompt = f.read()

        with open("prompt/system_classify_action_prompt.txt", "r") as f:
            self.classify_action_system_prompt = f.read()

        with open("prompt/user_classify_action_prompt.txt", "r") as f:
            self.classify_action_user_prompt_template = f.read()

    def update_state(self, response: AIResponseSuccess):
        self.state.player.health += response.health_change
        self.state.player.inventory.update(response.inventory_changes)

        # Update history
        self.state.floor_history[self.state.current_floor].add_narrative(
            response.respond_message
        )

        # TODO: In here, let's AI to generate summary asynchronously
        if response.next_floor:
            self.state.current_floor += 1

    def setup_floor_user_prompt(self):
        floor_type = "Combat" if self.state.current_floor % 2 == 0 else "Non-combat"
        return self.describe_floor_system_prompt.format(
            current_floor=self.state.current_floor,
            floor_type=floor_type,
            history=self.state.format_history(),
        )

    def generate_floor_description_response(self) -> AIResponse:
        """Generate a description of the current floor using the LLM"""

        llm_response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": self.respond_system_prompt},
                {"role": "user", "content": self.setup_floor_user_prompt()},
            ],
            response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "respond_message": {"type": "string"},
                        "suggested_actions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "health_change": {"type": "number"},
                        "next_floor": {"type": "boolean"},
                        "inventory_changes": {"type": "object"},
                        "game_over": {"type": "boolean"},
                    },
                    "required": [
                        "respond_message",
                        "suggested_actions",
                        "health_change",
                        "next_floor",
                        "inventory_changes",
                        "game_over",
                    ],
                },
            },
            temperature=0.8,
            max_tokens=500,
        )["choices"][0]["message"]["content"].strip()

        return AIResponse.process_response(llm_response)

    def handle_ai_response(self, response: AIResponse):
        # TODO: Error handling
        if not response.success:
            print(response)
            return response

        else:
            self.update_state(response)
            return response

    def generate_floor_description(self):
        response = self.generate_floor_description_response()
        self.handle_ai_response(response)
        return response

    def setup_player_action_prompt(self, player_input: str):
        return f"""Game State:
        - Floor: {self.state.current_floor}
        - Health: {self.state.player.health}
        - Inventory: {json.dumps(self.state.player.inventory)}
        
        Previous context: {self.state.game_context[-1000:]}
        
        Player action: {player_input}
        
        Respond to the player's action. Update the game state as needed. Be concise but descriptive.
        If the player defeats a floor boss or completes a major objective, mention that they can proceed to the next floor.
        """

    def process_player_action(self, player_input: str) -> str:
        """Process player input and return the game's response"""
        prompt = self.setup_player_action_prompt(player_input)
        llm_response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": self.describe_floor_system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.8,
        )["choices"][0]["message"]["content"].strip()

        response = self.process_response(llm_response)
        self.update_state(response)

        return response

    def setup_classify_action_user_prompt(self, player_input: str):
        return self.classify_action_user_prompt_template.format(
            player_input=player_input,
            current_floor=self.state.current_floor,
            floor_type="Combat" if self.state.current_floor % 2 == 0 else "Non-combat",
            history=self.state.format_history(),
            player_stats=self.state.player.__dict__,
        )

    def classify_action(self, action: str):
        """Classify the player's action and return the game's response"""

        # Get the AI's analysis
        llm_respond: str = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": self.classify_action_system_prompt},
                {
                    "role": "user",
                    "content": self.setup_classify_action_user_prompt(action),
                },
            ],
            response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "narrative_consistency": {"type": "boolean"},
                        "action_type": {
                            "type": "string",
                            "enum": ["ability_check", "use_item", "go_to_next_floor"],
                        },
                        "relevant_attribute": {
                            "type": "string",
                            "enum": [
                                "strength",
                                "dexterity",
                                "intelligence",
                                "wisdom",
                                "charisma",
                            ],
                        },
                        "difficulty_class": {
                            "type": "number",
                            "minimum": 3,
                            "maximum": 11,
                        },
                        "success_response": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"},
                                "is_event_end": {"type": "boolean"},
                                "suggested_actions": {"type": "array", "items": {"type": "string"}},
                                "health_change": {"type": "number"},
                                "inventory_changes": {"type": "object"},
                                "attribute_changes": {"type": "object"},
                            },
                            "required": [
                                "message",
                                "is_event_end",
                                "suggested_actions",
                                "health_change",
                                "inventory_changes",
                                "attribute_changes",
                            ],
                        },
                        "failure_response": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"},
                                "is_event_end": {"type": "boolean"},
                                "suggested_actions": {"type": "array", "items": {"type": "string"}},
                                "health_change": {"type": "number"},
                                "inventory_changes": {"type": "object"},
                                "attribute_changes": {"type": "object"},
                            },
                            "required": [
                                "message",
                                "is_event_end",
                                "suggested_actions",
                                "health_change",
                                "inventory_changes",
                                "attribute_changes",
                            ],
                        },
                    },
                    "required": [
                        "narrative_consistency",
                        "action_type",
                        "relevant_attribute",
                        "difficulty_class",
                        "success_response",
                        "failure_response",
                    ],
                },
            },
            max_tokens=1000,
            temperature=0.8,
        )["choices"][0]["message"]["content"].strip()

        # Process the response
        return ClassifyActionResponse.process_response(action, llm_respond)

    def handle_action_consequence(self, action_consequence: ActionConsequence):
        self.state.player.health += action_consequence.health_change
        self.state.player.inventory.update(action_consequence.inventory_changes)
        self.state.player.update_attributes(action_consequence.attribute_changes)

        self.state.floor_history[self.state.current_floor].add_narrative(
            action_consequence.message
        )
    
    def _handle_action_response_success(self, response: ClassifyActionResponse):
        """By pass all the checking"""

        self.state.floor_history[self.state.current_floor].add_player_actions(
            response.player_action, True
        )
        self.handle_action_consequence(response.success_response)
    
    def _handle_action_response_failure(self, response: ClassifyActionResponse):
        """By pass all the checking"""

        self.state.floor_history[self.state.current_floor].add_player_actions(
            response.player_action, False
        )
        self.handle_action_consequence(response.failure_response)

    def handle_classify_action_response(self, response: ClassifyActionResponse):
        if isinstance(response, ClassifyActionSuccess):
            dc = response.difficulty_class
            relevant_attribute = response.relevant_attribute

            # Roll dice
            roll = random.randint(1, 10)

            # Calculate the result
            score = roll + getattr(self.state.player, relevant_attribute)

            # Check the result
            # Check critical success
            if roll == 10:
                # Success
                self._handle_action_response_success(response)

            # Check critical failure
            elif roll == 1:
                # Failure
                self._handle_action_response_failure(response)

            # Check score > dc or not
            elif score >= dc:
                # Success
                self._handle_action_response_success(response)

            else:
                # Failure
                self._handle_action_response_failure(response)

            return response

        elif isinstance(response, ClassifyActionNarrativeInconsistency):
            # TODO: Handle the narrative inconsistency
            return

        else:
            # TODO: Handle other error
            return response

    def start_game(self):
        # Initialize the first floor history
        self.state.floor_history[self.state.current_floor] = FloorHistory()
