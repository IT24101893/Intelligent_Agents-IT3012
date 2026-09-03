# agent.py
import random

class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        wall_ahead = percept.get('wall_ahead', False)
        food_here = percept.get('food_here', False)

        if food_here:
            return 'Right'
        if wall_ahead:
            return 'Left'
        return 'Right'

class ModelBasedAgent:
    def __init__(self):
        self.last_action = None
        self.action_cycle = ['Left', 'Right', 'Down', 'Up']

    def sense_and_act(self, percept: dict) -> str:
        wall_ahead = percept.get('wall_ahead', False)
    
        if wall_ahead:
            if self.last_action in self.action_cycle:
                idx = self.action_cycle.index(self.last_action)
                action = self.action_cycle[(idx + 1) % len(self.action_cycle)]
            else:
                action = self.action_cycle[0]
        else:
             action = self.last_action if self.last_action else 'Right'

        self.last_action = action
        return action

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)
    


