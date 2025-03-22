from collections import deque


class GameGraph:
    def __init__(self):
        self.graph = {}
        self.explored = set()

    def add_node(self, state):
        if state not in self.graph:
            self.graph[state] = []

    def add_edge(self, parent_state, child_state):
        if child_state not in self.graph[parent_state]:
            self.graph[parent_state].append(child_state)

    def heuristic_evaluation(self, state):
        stones_left, player1_stones, player2_stones, player1_points, player2_points, is_player_turn = state
        return (player2_points - player1_points) + (player2_stones - player1_stones) + \
               (2 if stones_left > 0 and stones_left % 2 == (0 if is_player_turn == 1 else 1) else 0)

    def build_graph(self, stones, player1_stones=0, player2_stones=0, player1_points=0, player2_points=0, player=1):
        queue = deque()
        root_state = (stones, player1_stones, player2_stones, player1_points, player2_points, player)
        queue.append(root_state)
        self.explored.add(root_state)
        self.add_node(root_state)

        while queue:
            current_state = queue.popleft()
            stones_left, p1_s, p2_s, p1_p, p2_p, current_player = current_state

            if stones_left == 0:
                continue

            for move in [2, 3]:
                if stones_left >= move:
                    new_stones = stones_left - move

                    if new_stones == 0:
                        if current_player == 1:
                            new_state = (new_stones, p1_s, p2_s, p1_p + move, p2_p, 2)
                        else:
                            new_state = (new_stones, p1_s, p2_s, p1_p, p2_p + move, 1)
                    else:
                        if new_stones % 2 == 0:
                            if current_player == 1:
                                new_state = (new_stones, p1_s + move, p2_s, p1_p, p2_p + 2, 2)
                            else:
                                new_state = (new_stones, p1_s, p2_s + move, p1_p + 2, p2_p, 1)
                        else:
                            if current_player == 1:
                                new_state = (new_stones, p1_s + move, p2_s, p1_p + 2, p2_p, 2)
                            else:
                                new_state = (new_stones, p1_s, p2_s + move, p1_p, p2_p + 2, 1)

                    self.add_node(new_state)
                    self.add_edge(current_state, new_state)

                    if new_state not in self.explored:
                        queue.append(new_state)
                        self.explored.add(new_state)

    def minimax(self, state, depth, max_depth, maximizing_player, cache):
        if state in cache:
            return cache[state]

        if depth == max_depth or state[0] == 0:
            score = self.heuristic_evaluation(state)
            cache[state] = score
            return score

        children = self.graph.get(state, [])
        if not children:
            return self.heuristic_evaluation(state)

        if maximizing_player:
            best_val = float('-inf')
            for child in children:
                val = self.minimax(child, depth + 1, max_depth, False, cache)
                best_val = max(best_val, val)
        else:
            best_val = float('inf')
            for child in children:
                val = self.minimax(child, depth + 1, max_depth, True, cache)
                best_val = min(best_val, val)

        cache[state] = best_val
        return best_val

    def best_move(self, state, max_depth=3):
        children = self.graph.get(state, [])
        if not children:
            return None

        best_child = None
        best_val = float('-inf') if state[5] == 2 else float('inf')
        cache = {}

        for child in children:
            val = self.minimax(child, 1, max_depth, state[5] == 1, cache)
            if (state[5] == 2 and val > best_val) or (state[5] == 1 and val < best_val):
                best_val = val
                best_child = child

        return best_child
    def alpha_beta(self, state, depth, max_depth, alpha, beta, maximizing_player):
        if depth == max_depth or state[0] == 0:
            return self.heuristic_evaluation(state)

        children = self.graph.get(state, [])
        if not children:
            return self.heuristic_evaluation(state)

        if maximizing_player:
            value = float('-inf')
            for child in children:
                value = max(value, self.alpha_beta(child, depth + 1, max_depth, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = float('inf')
            for child in children:
                value = min(value, self.alpha_beta(child, depth + 1, max_depth, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def best_move_alpha_beta(self, state, max_depth=3):
        children = self.graph.get(state, [])
        if not children:
            return None

        best_val = float('-inf') if state[5] == 2 else float('inf')
        best_child = None

        for child in children:
            val = self.alpha_beta(child, 1, max_depth, float('-inf'), float('inf'), state[5] == 2)
            if (state[5] == 2 and val > best_val) or (state[5] == 1 and val < best_val):
                best_val = val
                best_child = child

        return best_child


def play_game(stones, first_player, algorithm_choice):
    game_graph = GameGraph()
    game_graph.build_graph(stones, player=first_player)

    state = (stones, 0, 0, 0, 0, first_player)

    while state[0] > 0:
        print(f"Current state: {state}")

        if state[0] in [2, 3]:
            move = state[0]
            if state[5] == 1:
                state = (0, state[1], state[2], state[3] + move, state[4], 2)
            else:
                state = (0, state[1], state[2], state[3], state[4] + move, 1)
            break

        if state[5] == 1:
            move = int(input("Your move (2 or 3): "))
            if move not in [2, 3] or state[0] < move:
                print("Invalid move! Try again.")
                continue

            new_stones = state[0] - move
            if new_stones == 0:
                state = (new_stones, state[1], state[2], state[3] + move, state[4], 2)
            elif new_stones % 2 == 0:
                state = (new_stones, state[1] + move, state[2], state[3], state[4] + 2, 2)
            else:
                state = (new_stones, state[1] + move, state[2], state[3] + 2, state[4], 2)

        else:
            print("Computer is thinking...")
            if algorithm_choice == 1:
                state = game_graph.best_move(state, 3) or state
            else:
                state = game_graph.best_move_alpha_beta(state, 3) or state

    stones_left, p1_s, p2_s, p1_p, p2_p, pl = state
    final_p1 = p1_s + p1_p
    final_p2 = p2_s + p2_p
    print("\n--- Game Over ---")
    print(f"Player: {final_p1}, Computer: {final_p2}")
    if final_p1 > final_p2:
        print("Player wins!")
    elif final_p2 > final_p1:
        print("Computer wins!")
    else:
        print("It's a tie!")


def get_valid_input(prompt, valid_range):
    while True:
        try:
            value = int(input(prompt))
            if value in valid_range:
                return value
            else:
                print(f"Please enter a valid number: {valid_range}")
        except ValueError:
            print("Invalid input! Please enter a number.")


if __name__ == "__main__":
    while True:
        stones = get_valid_input("Enter the number of stones to start (50-70): ", range(50, 71))
        first_player = get_valid_input("Who starts? (1 - You, 2 - Computer): ", [1, 2])
        algorithm_choice = get_valid_input("Choose AI algorithm (1 - Minimax, 2 - Alpha-Beta Pruning): ", [1, 2])

        play_game(stones, first_player, algorithm_choice)
        restart = input("Do you want to play again? (yes/no): ").strip().lower()
        if restart not in ["yes", "y"]:
            print("Thanks for playing! Goodbye!")
            break