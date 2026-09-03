
# agent.py
import random
from collections import deque
import heapq
import math


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
        self.active_algo = 'AStar'

    def manhattan_distance(self, pos, goal):
        """Calculate Manhattan distance between two positions."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """Calculate Euclidean distance between two positions."""
        return math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
        )

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

            for next_pos, action in self.get_neighbors(
                current, walls, grid_size
            ):
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

            for next_pos, action in self.get_neighbors(
                current, walls, grid_size
            ):
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

            for next_pos, action in self.get_neighbors(
                current, walls, grid_size
            ):
                new_cost = cost + 1

                if next_pos not in reached or new_cost < reached[next_pos]:
                    reached[next_pos] = new_cost
                    counter += 1
                    heapq.heappush(
                        priority_queue,
                        (new_cost, counter, next_pos, path + [action])
                    )

        return None

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):
        """Find the shortest path using A* Search."""

        priority_queue = []
        reached_states = set()
        counter = 0

        # Calculate initial heuristic
        if heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(start_pos, goal_pos)
        else:
            h_cost = self.manhattan_distance(start_pos, goal_pos)

        # Starting node: f = g + h
        g_cost = 0
        f_cost = g_cost + h_cost

        heapq.heappush(
            priority_queue,
            (f_cost, g_cost, counter, start_pos, [])
        )

        while priority_queue:

            f_cost, g_cost, _, current_pos, path_taken = heapq.heappop(
                priority_queue
            )

            # Goal reached
            if current_pos == goal_pos:
                return path_taken

            # Skip already expanded states
            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            # Expand neighboring cells
            for next_pos, action in self.get_neighbors(
                current_pos,
                walls,
                grid_size
            ):

                if next_pos in reached_states:
                    continue

                # Every movement costs 1
                new_g_cost = g_cost + 1

                # Calculate heuristic
                if heuristic_type == 'euclidean':
                    new_h_cost = self.euclidean_distance(
                        next_pos,
                        goal_pos
                    )
                else:
                    new_h_cost = self.manhattan_distance(
                        next_pos,
                        goal_pos
                    )

                # A* evaluation function
                new_f_cost = new_g_cost + new_h_cost

                counter += 1

                heapq.heappush(
                    priority_queue,
                    (
                        new_f_cost,
                        new_g_cost,
                        counter,
                        next_pos,
                        path_taken + [action]
                    )
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
            elif self.active_algo == 'AStar':
             path = self.astar_search(
                start,
                goal,
                walls,
                grid_size,
                heuristic_type='manhattan'
    )
            else:
                path = None

            if path:
                self.plan = path

        if self.plan:
            return self.plan.pop(0)

        return 'Right'


if __name__ == "__main__":
    agent = SearchAgent()

    start = (0, 0)
    goal = (3, 4)

    print("Manhattan Distance:", agent.manhattan_distance(start, goal))
    print("Euclidean Distance:", agent.euclidean_distance(start, goal))


# PS C:\Users\Acer\Desktop\IT3012---Practical-Base> python agent.py
# Manhattan Distance: 7
# Euclidean Distance: 5.0


if __name__ == "__main__":
    agent = SearchAgent()

    grid_size = (4, 4)

    start = (0, 0)
    goal = (3, 3)

    walls = {
        (1, 0),
        (2, 0),
        (0, 2),
        (1, 2),
        (2, 2)
    }

    path = agent.astar_search(
        start,
        goal,
        walls,
        grid_size,
        heuristic_type='manhattan'
    )

    print("A* Path:", path)
    print("A* Path Length:", len(path) if path else None)

#A* Path: ['Up', 'Right', 'Right', 'Right', 'Up', 'Up']
#A* Path Length: 6