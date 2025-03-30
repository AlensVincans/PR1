from collections import deque
import time
import pygame

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
    
    def print_graph(self):
        for node, children in self.graph.items():
            print(f"{node} --> {children}")

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
            best_val = float('-1')
            for child in children:
                val = self.minimax(child, depth + 1, max_depth, False, cache)
                best_val = max(best_val, val)
        else:
            best_val = float('1')
            for child in children:
                val = self.minimax(child, depth + 1, max_depth, True, cache)
                best_val = min(best_val, val)

        cache[state] = best_val
        return best_val
    
    def best_move_combined(self, state, max_depth=3, use_alpha_beta=False):
        children = self.graph.get(state, [])
        if not children:
            return None

        best_val = float('-1') if state[5] == 2 else float('1')
        best_child = None
        cache = {}

        for child in children:
            if use_alpha_beta:
                val = self.alpha_beta(child, 1, max_depth, float('-1'), float('1'), state[5] == 2)
            else:
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
            value = float('-1')
            for child in children:
                value = max(value, self.alpha_beta(child, depth + 1, max_depth, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = float('1')
            for child in children:
                value = min(value, self.alpha_beta(child, depth + 1, max_depth, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

def play_game(stones, first_player, algorithm_choice):

    computer_move_times = []

    game_graph = GameGraph()
    game_graph.build_graph(stones, player=first_player)

    state = (stones, 0, 0, 0, 0, first_player)

    while state[0] > 0:
        print(f"Spēles stāvoklis: {state}")

        if state[0] == 1:
            if state[5] == 1:
                state = (0, state[1], state[2] + 1, state[3], state[4], 1)
            else:
                state = (0, state[1] + 1, state[2], state[3], state[4], 2)
            break

        if state[0] in [2, 3]:
            if state[0] in [1, 2]:
                remaining = state[0]
                if state[5] == 1:
                    state = (0, state[1], state[2] + remaining, state[3], state[4], 1)
                else:
                    state = (0, state[1] + remaining, state[2], state[3], state[4], 2)
                break


        if state[5] == 1:
            move = int(input("Jūsu gājiens (2 vai 3): "))
            if move not in [2, 3] or state[0] < move:
                print("Nederīgs gājiens! Mēģini vēlreiz.")
                continue

            new_stones = state[0] - move
            if new_stones == 0:
                state = (new_stones, state[1], state[2], state[3] + move, state[4], 2)
            elif new_stones % 2 == 0:
                state = (new_stones, state[1] + move, state[2], state[3], state[4] + 2, 2)
            else:
                state = (new_stones, state[1] + move, state[2], state[3] + 2, state[4], 2)

        else:
            start_time = time.time()

            use_alpha_beta = (algorithm_choice == 2)
            state = game_graph.best_move_combined(state, 3, use_alpha_beta) or state

            end_time = time.time()
            elapsed_time = end_time - start_time
            computer_move_times.append(elapsed_time)

            print(f"Datora gājiena laiks: {elapsed_time:.4f} seconds")

    if computer_move_times:
        avg_time = sum(computer_move_times) / len(computer_move_times)
        print(f"\nVidējais datora gājiena laiks: {avg_time:.4f} seconds")


    stones_left, p1_s, p2_s, p1_p, p2_p, pl = state
    final_p1 = p1_s + p1_p
    final_p2 = p2_s + p2_p
    print("\n--- Game Over ---")
    print(f"Speletājs: {final_p1}, Dators: {final_p2}")
    if final_p1 > final_p2:
        print("Spēlētājs uzvar!")
    elif final_p2 > final_p1:
        print("Dators uzvar!")
    else:
        print("Spēle beidzās neizšķirti!")


def get_valid_input(prompt, valid_range):
    while True:
        try:
            value = int(input(prompt))
            if value in valid_range:
                return value
            else:
                print(f"Please enter a valid number: {valid_range}")
        except ValueError:
            print("Lūdzu, ievadiet derīgu skaitli: ")


if __name__ == "__main__":
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Stone Game GUI")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    BLUE = (50, 50, 255)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)

    FONT = pygame.font.SysFont("arial", 24)

    stones = 50
    first_player = 1
    algorithm_choice = 1

    game_state = None
    game_graph = None
    final_scores = None
    winner_message = ""
    moves_log = []
    mode = "menu"

    def draw_button(text, rect, color=GRAY, text_color=BLACK):
        pygame.draw.rect(screen, color, rect)
        txt_surf = FONT.render(text, True, text_color)
        txt_rect = txt_surf.get_rect(center=rect.center)
        screen.blit(txt_surf, txt_rect)
        return rect

    def create_log_entry(actor, move, new_stones):
        if new_stones == 0:
            return f"{actor} ended the game by taking {move} stones, gaining {move} points."
        elif new_stones % 2 == 0:
            return f"{actor} took {move} stones on an even board; no bonus for {actor} (opponent gets +2)."
        else:
            return f"{actor} took {move} stones on an odd board and got +2 bonus points."

    def draw_menu():
        screen.fill(WHITE)
        title = FONT.render("Game Setup", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        stones_text = FONT.render(f"Number of Stones: {stones}", True, BLACK)
        screen.blit(stones_text, (100, 150))
        dec_rect = pygame.Rect(350, 150, 50, 40)
        inc_rect = pygame.Rect(420, 150, 50, 40)
        draw_button("-", dec_rect)
        draw_button("+", inc_rect)
        turn_text = FONT.render("Who goes first?", True, BLACK)
        screen.blit(turn_text, (100, 220))
        player_rect = pygame.Rect(100, 260, 150, 40)
        comp_rect = pygame.Rect(270, 260, 150, 40)
        p_color = GREEN if first_player == 1 else GRAY
        c_color = GREEN if first_player == 2 else GRAY
        draw_button("Player", player_rect, color=p_color, text_color=WHITE)
        draw_button("Computer", comp_rect, color=c_color, text_color=WHITE)
        ai_text = FONT.render("Choose AI Algorithm:", True, BLACK)
        screen.blit(ai_text, (100, 330))
        minimax_rect = pygame.Rect(100, 370, 150, 40)
        alphabeta_rect = pygame.Rect(270, 370, 150, 40)
        m_color = GREEN if algorithm_choice == 1 else GRAY
        ab_color = GREEN if algorithm_choice == 2 else GRAY
        draw_button("Minimax", minimax_rect, color=m_color, text_color=WHITE)
        draw_button("Alpha-Beta", alphabeta_rect, color=ab_color, text_color=WHITE)
        start_rect = pygame.Rect(WIDTH//2 - 75, 450, 150, 50)
        draw_button("Start Game", start_rect, color=BLUE, text_color=WHITE)
        return {
            "decrease": dec_rect,
            "increase": inc_rect,
            "player": player_rect,
            "computer": comp_rect,
            "minimax": minimax_rect,
            "alphabeta": alphabeta_rect,
            "start": start_rect
        }

    def draw_game():
        screen.fill(WHITE)
        state_txt = FONT.render(f"State: {game_state}", True, BLACK)
        screen.blit(state_txt, (20, 20))
        turn = "Player" if game_state[5] == 1 else "Computer"
        turn_txt = FONT.render(f"Turn: {turn}", True, BLACK)
        screen.blit(turn_txt, (20, 60))
        p1_total = game_state[1] + game_state[3]
        p2_total = game_state[2] + game_state[4]
        points_text = FONT.render(f"Player Points: {p1_total}    Computer Points: {p2_total}", True, BLACK)
        screen.blit(points_text, (20, 100))
        log_title = FONT.render("Last Moves:", True, BLACK)
        screen.blit(log_title, (20, 140))
        for i, entry in enumerate(moves_log):
            log_entry_text = FONT.render(entry, True, BLACK)
            screen.blit(log_entry_text, (20, 170 + i * 30))
        buttons = {}
        if game_state[5] == 1:
            btn2 = pygame.Rect(100, 500, 150, 50)
            btn3 = pygame.Rect(300, 500, 150, 50)
            if game_state[0] >= 2:
                draw_button("Take 2", btn2, color=GREEN, text_color=WHITE)
            else:
                draw_button("Take 2", btn2, color=GRAY)
            if game_state[0] >= 3:
                draw_button("Take 3", btn3, color=GREEN, text_color=WHITE)
            else:
                draw_button("Take 3", btn3, color=GRAY)
            buttons["move2"] = btn2
            buttons["move3"] = btn3
        else:
            thinking_txt = FONT.render("Computer is thinking...", True, BLACK)
            screen.blit(thinking_txt, (100, 500))
        return buttons

    def draw_game_over():
        screen.fill(WHITE)
        over_txt = FONT.render("Game Over!", True, RED)
        screen.blit(over_txt, (WIDTH//2 - over_txt.get_width()//2, 100))
        if final_scores:
            score_txt = FONT.render(f"Player: {final_scores[0]}    Computer: {final_scores[1]}", True, BLACK)
            screen.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, 200))
        win_txt = FONT.render(winner_message, True, BLACK)
        screen.blit(win_txt, (WIDTH//2 - win_txt.get_width()//2, 250))
        play_again_rect = pygame.Rect(WIDTH//2 - 75, 350, 150, 50)
        draw_button("Play Again", play_again_rect, color=BLUE, text_color=WHITE)
        return {"play_again": play_again_rect}

    def player_move(move):
        global game_state, moves_log
        old_state = game_state
        stones_left, p1_s, p2_s, p1_p, p2_p, current_player = game_state
        if move not in [2, 3] or stones_left < move:
            return
        new_stones = stones_left - move
        if new_stones == 0:
            if current_player == 1:
                game_state = (new_stones, p1_s, p2_s, p1_p + move, p2_p, 2)
            else:
                game_state = (new_stones, p1_s + move, p2_s, p1_p, p2_p + move, 1)
        elif new_stones % 2 == 0:
            if current_player == 1:
                game_state = (new_stones, p1_s + move, p2_s, p1_p, p2_p + 2, 2)
            else:
                game_state = (new_stones, p1_s, p2_s + move, p1_p + 2, p2_p, 1)
        else:
            if current_player == 1:
                game_state = (new_stones, p1_s + move, p2_s, p1_p + 2, p2_p, 2)
            else:
                game_state = (new_stones, p1_s, p2_s + move, p1_p, p2_p + 2, 1)
        actor = "Player" if current_player == 1 else "Computer"
        log_entry = create_log_entry(actor, move, new_stones)
        moves_log.append(log_entry)
        if len(moves_log) > 2:
            moves_log.pop(0)

    def check_game_over():
        global game_state, final_scores, winner_message
        if game_state[0] == 0:
            stones_left, p1_s, p2_s, p1_p, p2_p, current_player = game_state
            final_p1 = p1_s + p1_p
            final_p2 = p2_s + p2_p
            final_scores = (final_p1, final_p2)
            if final_p1 > final_p2:
                winner_message = "Player wins!"
            elif final_p2 > final_p1:
                winner_message = "Computer wins!"
            else:
                winner_message = "It's a tie!"
            return True
        return False

    clock = pygame.time.Clock()
    running = True
    menu_buttons = {}
    game_buttons = {}
    game_over_buttons = {}
    computer_move_in_progress = False

    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if mode == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if menu_buttons["decrease"].collidepoint(mx, my) and stones > 50:
                    stones -= 1
                if menu_buttons["increase"].collidepoint(mx, my) and stones < 70:
                    stones += 1
                if menu_buttons["player"].collidepoint(mx, my):
                    first_player = 1
                if menu_buttons["computer"].collidepoint(mx, my):
                    first_player = 2
                if menu_buttons["minimax"].collidepoint(mx, my):
                    algorithm_choice = 1
                if menu_buttons["alphabeta"].collidepoint(mx, my):
                    algorithm_choice = 2
                if menu_buttons["start"].collidepoint(mx, my):
                    game_graph = GameGraph()
                    game_graph.build_graph(stones, player=first_player)
                    game_state = (stones, 0, 0, 0, 0, first_player)
                    moves_log = []
                    mode = "game"
            if mode == "game" and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if game_state[5] == 1:
                    if "move2" in game_buttons and game_buttons["move2"].collidepoint(mx, my):
                        player_move(2)
                    if "move3" in game_buttons and game_buttons["move3"].collidepoint(mx, my):
                        player_move(3)
            if mode == "game_over" and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if game_over_buttons["play_again"].collidepoint(mx, my):
                    mode = "menu"
        if mode == "menu":
            menu_buttons = draw_menu()
        elif mode == "game":
            if check_game_over():
                mode = "game_over"
            else:
                if game_state[5] == 2 and not computer_move_in_progress:
                    computer_move_in_progress = True
                    old_state = game_state
                    pygame.display.update()
                    pygame.time.delay(500)
                    start_time = time.time()
                    use_alpha_beta = (algorithm_choice == 2)
                    next_state = game_graph.best_move_combined(game_state, max_depth=3, use_alpha_beta=use_alpha_beta)
                    if next_state is not None:
                        move_taken = game_state[0] - next_state[0]
                        game_state = next_state
                        log_entry = create_log_entry("Computer", move_taken, game_state[0])
                        moves_log.append(log_entry)
                        if len(moves_log) > 2:
                            moves_log.pop(0)
                    end_time = time.time()
                    print(f"Computer move took {end_time - start_time:.4f} seconds")
                    computer_move_in_progress = False
                game_buttons = draw_game()
        elif mode == "game_over":
            game_over_buttons = draw_game_over()
        pygame.display.update()

    pygame.quit()
