class GameGraph:
    def __init__(self):
        self.graph = {}  # {state: [possible transitions]}
        self.explored = set()  # To avoid duplicating states

    def add_node(self, state):
        if state not in self.graph:
            self.graph[state] = []

    def add_edge(self, parent_state, child_state):
        if child_state not in self.graph[parent_state]:
            self.graph[parent_state].append(child_state)

    def build_graph(self, stones, p1_stones=0, p2_stones=0, p1_points=0, p2_points=0, player=1):
        current_state = (stones, p1_stones, p2_stones, p1_points, p2_points, player)
        
        if current_state in self.explored:
            return
        self.explored.add(current_state)
        self.add_node(current_state)

        # Base Case: Game Over
        if stones == 0:
            final_p1 = p1_points + p1_stones
            final_p2 = p2_points + p2_stones
            self.graph[current_state] = [f"Game Over: P1={final_p1}, P2={final_p2}, Winner: {"P1" if final_p1 > final_p2 else ("P2" if final_p2 > final_p1 else "draw")}"]
            return
        
        if stones == 1:
            if player == 1:
                final_p1 = p1_points + p1_stones + 1
                final_p2 = p2_points + p2_stones
            else:
                final_p1 = p1_points + p1_stones
                final_p2 = p2_points + p2_stones + 1
            self.graph[current_state] = [f"Game Over: P1={final_p1}, P2={final_p2}, Winner: {"P1" if final_p1 > final_p2 else ("P2" if final_p2 > final_p1 else "draw")}"]
            return
        
        # Explore moves: 2 and 3 stones
        for move in [2, 3]:
            if stones >= move:
                new_stones = stones - move
                if new_stones % 2 == 0:
                    if player == 1:
                        new_state = (new_stones, p1_stones + move, p2_stones, p1_points, p2_points + 2, 2)
                    else:
                        new_state = (new_stones, p1_stones, p2_stones + move, p1_points + 2, p2_points, 1)
                else:
                    if player == 1:
                        new_state = (new_stones, p1_stones + move, p2_stones, p1_points + 2, p2_points, 2)
                    else:
                        new_state = (new_stones, p1_stones, p2_stones + move, p1_points, p2_points + 2, 1)

                self.add_node(new_state)
                self.add_edge(current_state, new_state)
                self.build_graph(new_stones, *new_state[1:5], player=new_state[5])

    def print_graph(self):
        for node, children in self.graph.items():
            print(f"{node} --> {children}")


################ MAIN ################

stones = int(input("Izvēlies akmentiņu skaitu spēles sākumam (no 50 līdz 70): "))
while not (50 <= stones <= 70):
    stones = int(input("Lūdzu ievadi skaitu no 50 līdz 70: "))

# Choose who starts the game
first_player = int(input("Kurš uzsāk spēli? (1 - cilvēks, 2 - dators): "))
while first_player not in [1, 2]:
    first_player = int(input("Lūdzu ievadi '1' (cilvēks) vai '2' (dators): "))

game_graph = GameGraph()
game_graph.build_graph(stones, player=first_player)
game_graph.print_graph()
