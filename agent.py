# agent.py
import random
from collections import deque
import heapq

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

class SearchAgent:
    def __init__(self):
        self.plan = []
        self.active_algo = 'UCS'

    def get_neighbors(self, position, walls, grid_size):
        x, y = position
        width, height = grid_size

        moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]

        neighbors = []

        for action, new_pos in moves:
            nx, ny = new_pos

            if 0 <= nx < width and 0 <= ny < height:
                if new_pos not in walls:
                    neighbors.append((new_pos, action))

        return neighbors

    def bfs_search(self, start, goal, walls, grid_size):
        queue = deque([(start, [])])
        reached = {start}

        while queue:
            current, path = queue.popleft()

            if current == goal:
                return path

            for next_pos, action in self.get_neighbors(current, walls, grid_size):
                if next_pos not in reached:
                    reached.add(next_pos)
                    queue.append((next_pos, path + [action]))

        return None

    def dfs_search(self, start, goal, walls, grid_size):
        stack = [(start, [])]
        reached = {start}

        while stack:
            current, path = stack.pop()

            if current == goal:
                return path

            for next_pos, action in self.get_neighbors(current, walls, grid_size):
                if next_pos not in reached:
                    reached.add(next_pos)
                    stack.append((next_pos, path + [action]))

        return None

    def ucs_search(self, start, goal, walls, grid_size):
        priority_queue = [(0, 0, start, [])]
        reached = {start: 0}
        counter = 0

        while priority_queue:
            cost, _, current, path = heapq.heappop(priority_queue)

            if current == goal:
                return path

            for next_pos, action in self.get_neighbors(current, walls, grid_size):
                new_cost = cost + 1

                if next_pos not in reached or new_cost < reached[next_pos]:
                    reached[next_pos] = new_cost
                    counter += 1
                    heapq.heappush(
                        priority_queue,
                        (new_cost, counter, next_pos, path + [action])
                    )

        return None

    def sense_and_act(self, percept):
        if not self.plan:
            start = tuple(percept['agent_pos']) if 'agent_pos' in percept else None

            if start is None:
                # The visual environment currently doesn't expose agent_pos,
                # so use the default starting position.
                start = (0, 0)

            food_positions = percept['all_food']
            walls = set(percept['walls'])
            grid_size = percept['grid_size']

            if not food_positions:
                return 'Stay'

            # Find the closest food using Manhattan distance
            goal = min(
                food_positions,
                key=lambda food: abs(food[0] - start[0]) + abs(food[1] - start[1])
            )

            if self.active_algo == 'BFS':
                path = self.bfs_search(start, goal, walls, grid_size)
            elif self.active_algo == 'DFS':
                path = self.dfs_search(start, goal, walls, grid_size)
            elif self.active_algo == 'UCS':
                path = self.ucs_search(start, goal, walls, grid_size)
            else:
                path = None

            if path:
                self.plan = path

        if self.plan:
            return self.plan.pop(0)

        return 'Right'
    


