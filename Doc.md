# Game Plan
---
- We will have combat floors and non-combat floors alternately

## Non-combat floors
- Non-combat floors type are: 
  - Simple Reward floor
  - Reward with Trap floor 
  - Shop floor (skip it for the simplicity)

- For each floor, we will have only one event (for the sake of simplicity)
- If the LLM tells us that the event is over, we will force the player to move to the next floor (for the sake of simplicity too)
- There is an option for the player to skip the event 


## Combat floors
- Combat floors consists of one enemy (for the sake of simplicity)

# Game Logic
---
- When start game: 
  - Initialize `GameState`
  - send `BackgroundRequest` to get the background 

while not game over:
  - if current floor is non-combat floors:
    - get the floor type randomly by python
    - send `NonCombatFloorIntroRequest` to get the floor description and suggested actions
      - Update the history

    - wait for the player input
    - send `ClassifyNonCombatActionRequest` to classify the player's action
      - if the action is "go_to_next_floor", then we move to new floor -> end!!
      - if the action is "use_item", then just use the item.
        - Update the state 
        - The user prompt for `NonCombatStoryExtendRequest` may be "You use the {item.name} ({item.effect})." 

      - if the action is "ability_check", then we send out `AbilityCheckRequest` to get the related attribute and difficulty class
        - calculate it is successful or not in python
        - The user prompt for `NonCombatStoryExtendRequest` may be "{player_action}. It is successful / unsuccessful."
        - Update the roll result to the history

    - send `NonCombatStoryExtendRequest` based on the result
      - Update the history and state
      - If the event is over, send the `LootOrPunishmentRequest` to get the loot or punishment
        - Update the state
        - then move to new floor -> end!!
      - If it is not, keep looping above until the event is over -> move to new floor

  - if current floor is combat floors:
    - send `CombatFloorIntroRequest` to get the floor description, enemy
    - wait for the player input
    - send `ClassifyInitCombatActionRequest` to get the player action
    - calculate the action is success or not
      - if you choose to run away / persuasion / intimidation
        - if you success, send the corresponding request, then move to new floor -> end!!
      - if you choose to surprise attack
        - if you success, send the corresponding request, and enter combat mode with you as the first player
      - if you fail, send the corresponding request, and enter combat mode with the enemy as the first player

    - enter combat mode:
      - your turn: 
        - wait for your input
        - send `ClassifyCombatActionRequest` to classify the player action
          - if the action is "use_item", then just use the item.
            - Update the state 
          - The user prompt for `NonCombatStoryExtendRequest` may be "You use the {item.name} ({item.effect})."
        - for other actions, we send out `AbilityCheckRequest` to get the related attribute and difficulty class
          - calculate it is successful or not in python
          - if attack, send out `AttackStoryExtendRequest` to update the damage 
          - run_away/persuade/intimidate: similar to above
          - if the enemy is not defeated, and the player cannot leave the floor, enemy turn

      - enemy turn: 
        - send out `EnemyAttackStoryExtendRequest` to generate response to the player 
        - wait for the player to respond
        - send out `ClassifyDefendActionRequest` and calculate how successful it is 
        - send out `EnemyAttackPlayerRespondRequest` to update the damage 
        - player turn if the combat does not end
    
    - if the enemy is defeated:
      - send out `EnemyDefeatedRespondRequest` to get the loot
      - three fixed choices: get the loot / heal / attribute upgrade one point
      - move to new floor


# Classes
--- 

## Main Class 
- DungeonMaster
  - current_state: `GameState`
  - history: list of `FloorHistory`

## Important classes
- GameState
  - Floor
  - Player 

- FloorHistory

## Entity Classes
- Weapon
  - Name: str
  - Description: str (for LLM to test the prompt, the ability check)
  - Normal Damage: int (for the hint of the LLM)

- Item
  - Name: str
  - Effect: str

- Status effect (Skip it for the simplicity)

- Entity (including both player and enemy)
  - Description: str
  - Current Health
  - Max Health
  - Strength
  - Dexterity
  - Intelligence
  - Wisdom
  - Charisma

- Player(Entity)
  - Description: "Player"
  - Weapon: `Weapon`
  - Inventory in list of `Item`

- Enemy(Entity)
  - Description: str
  - Normal Damage: int

## Floor Classes
- Floor
  - Current floor
  - Floor type


## API Classes (for talking to LLM)
- AbstractRequest
  - setup_system_prompt()
  - setup_user_prompt()
  - memory: only using current floor history (for simplicity)
  - send() -> AbstractRespond
  - send_and_export(save_path: str) -> AbstractRespond


- BackgroundRequest -> BackgroundRespond 
  - Themes and background
  - Therefore we will have consistent theme for each floor


### Non-combat floors
- NonCombatFloorIntroRequest -> NonCombatFloorIntroRespond
  - Input the floor type (which is randomized by Python), 
  - Output the 
    - floor descriptions
    - suggested actions


- ClassifyNonCombatActionRequest -> ClassifyNonCombatActionRespond
  - Input: user_input
  - Output: Classify it is 
    - ability_check
    - use_item
    - go_to_next_floor


- AbilityCheckRequest -> AbilityCheckRespond
  - Input user_input
  - Output: 
    - What attribute it is related
    - The difficulty class


- NonCombatStoryExtendRequest -> NonCombatStoryExtendRespond 
  - Input user_input
  - Output:
    - narrative: the follow up story
    - health_change: the change of health
    - attribute_change: the change of attribute
    - is_event_end: whether the event is over
    - suggested actions


- LootOrPunishmentRequest -> LootOrPunishmentRespond
  - Let AI to determine the reward or punishment for the player based on the history
  - Input: the entire floor history
  - Output:
    - narrative: words to the player
    - Inventory changes: Get some practical items:


- CombatFloorIntroRequest -> CombatFloorIntroRespond
  - General floor description
  - Spawn one `Enemy`
    - Description
    - Current Health
    - Max Health
    - Strength
    - Dexterity
    - Intelligence
    - Wisdom
    - Charisma
    - Physical Damage
    - Ranged Damage
    - Magic Damage

  - Input: the last three enemies, ask AI to make it distinct to the last three enemies
  - Output: 
    - Three suggested actions, generated by AI
      - One is persuade/intimidate (Use Charisma Check)
      - One is surprise attack (Use Dexterity Check)
      - One is run away (Also use Dexterity Check)
  

- ClassifyInitCombatActionRequest -> ClassifyInitCombatActionRespond
  - Input user_input
  - Classify it is 
    - the action_type: 
      - persuade
      - intimidate
      - surprise attack
      - run away
    - the difficulty (it is judged by AI!!)


- PersuadeSuccessStoryExtendRequest -> PersuadeSuccessStoryExtendRespond
  - Input (roughly): "You persuade the enemy successfully."
  - Output:
    - narrative: the follow up story


- PersuadeFailStoryExtendRequest -> PersuadeFailStoryExtendRespond
  - Input (roughly): "You persuade the enemy unsuccessfully."
  - Output:
    - narrative: the follow up story


- IntimidateSuccessStoryExtendRequest -> IntimidateSuccessStoryExtendRespond
  - Input (roughly): "You intimidate the enemy successfully."
  - Output:
    - narrative: the follow up story


- IntimidateFailStoryExtendRequest -> IntimidateFailStoryExtendRespond
  - Input (roughly): "You intimidate the enemy unsuccessfully."
  - Output:
    - narrative: the follow up story


- RunAwaySuccessStoryExtendRequest -> RunAwaySuccessStoryExtendRespond
  - Input (roughly): "You run away successfully."
  - Output:
    - narrative: the follow up story


- RunAwayFailStoryExtendRequest -> RunAwayFailStoryExtendRespond
  - Input (roughly): "You run away unsuccessfully."
  - Output:
    - narrative: the follow up story


- SurpriseAttackSuccessStoryExtendRequest -> SurpriseAttackSuccessStoryExtendRespond
  - Input (roughly): "You surprise attack the enemy successfully."
  - Output:
    - narrative: the follow up story


- SurpriseAttackFailStoryExtendRequest -> SurpriseAttackFailStoryExtendRespond
  - Input (roughly): "You surprise attack the enemy unsuccessfully."
  - Output:
    - narrative: the follow up story


- ClassifyCombatActionRequest -> ClassifyCombatActionRespond
  - Input user_input
  - Classify it is 
    - the action_type: 
      - attack
      - use_item
      - persuade/intimidate
      - run_away
    - related_attribute
    - difficulty_class


- AttackStoryExtendRequest -> AttackStoryExtendRespond
  - Input 
    - Prompt is like "The player is going to attack the enemy" + how the player attacks the enemy
    - Player stat
    - weapon
    - Enemy stat
    - success/fail (calculate by python)

  - Output:
    - narrative: the follow up story
    - health_change: the change of health of enemy (judged by AI!! We will give the normal damage of the weapon. We let AI to judge the damage.)


- EnemyAttackStoryExtendRequest -> EnemyAttackStoryExtendRespond
  - Input: the enemy attack the player
  - Output:
    - narrative: the follow up story
    - two suggested actions
      - one is defend
      - one is dodge


- ClassifyDefendActionRequest -> ClassifyDefendActionRespond
  - Input user_input
  - Classify it is 
    - the action_type: 
      - defend
      - dodge
    - related_attribute and difficulty_class


- EnemyAttackPlayerRespondRequest -> EnemyAttackPlayerRespondRespond
  - Input 
    - Prompt is like 
      - How the enemy attack the player
      - "The player is going to defend / dodge the enemy, and it is successful / unsuccessful"
    - Player stat
    - Enemy damage 
    - Enemy stat

  - Output:
    - narrative: the follow up story
    - health_change: the change of health of player (judged by AI!! We will give the normal damage of the weapon. We let AI to judge the damage.)


- EnemyDefeatedRespondRequest -> EnemyDefeatedRespondRespond
  - Output:
    - narrative: how you do the final blow to the enemy
    - loot for player to choose: 
      - a better weapon? 
      - a item?


