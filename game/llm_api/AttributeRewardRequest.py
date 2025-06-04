from game.llm_api.LLMRequest import LLMResponseModel
from game.llm_api.ClassifyRewardTypeRequest import ClassifyRewardTypeRequest

from pydantic import Field
from typing import Literal


class AttributeRewardResponseModel(LLMResponseModel):
    attribute: Literal[
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"
    ] = Field(
        ...,
        description="The attribute to increase. Must be one of: strength, dexterity, constitution, intelligence, wisdom, or charisma.",
    )


class AttributeRewardRequest(ClassifyRewardTypeRequest):
    @property
    def prompt_file(self):
        return "attribute_reward.txt"

    @property
    def ResponseModel(self):
        return AttributeRewardResponseModel
