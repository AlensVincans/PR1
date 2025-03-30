import pygame
import sys
import time
from collections import deque

# -------------- SPĒLES LOĢIKA (SPĒLES GRAFS UN FUNKCIJAS) ----------------
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
        stones_left, p1_s, p2_s, p1_p, p2_p, is_player_turn = state
        return (
            (p2_p - p1_p)
            + (p2_s - p1_s)
            + (
                2
                if stones_left > 0
                and stones_left % 2 == (0 if is_player_turn == 1 else 1)
                else 0
            )
        )

    def build_graph(self, stones, player1_stones=0, player2_stones=0,
                    player1_points=0, player2_points=0, player=1):
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
                        # Paņemti pēdējie akmeņi
                        if current_player == 1:
                            new_state = (0, p1_s, p2_s, p1_p + move, p2_p, 2)
                        else:
                            new_state = (0, p1_s, p2_s, p1_p, p2_p + move, 1)
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

    def best_move_combined(self, state, max_depth=3, use_alpha_beta=False):
        children = self.graph.get(state, [])
        if not children:
            return None

        if state[5] == 1:
            best_val = float('inf')
            maximizing_player = False
        else:
            best_val = float('-inf')
            maximizing_player = True

        best_child = None
        cache = {}

        for child in children:
            if use_alpha_beta:
                val = self.alpha_beta(child, 1, max_depth, float('-inf'), float('inf'), maximizing_player)
            else:
                val = self.minimax(child, 1, max_depth, maximizing_player, cache)

            if maximizing_player and val > best_val:
                best_val = val
                best_child = child
            if not maximizing_player and val < best_val:
                best_val = val
                best_child = child

        return best_child

def get_valid_input(prompt, valid_range):
    return valid_range[0]

def play_game(stones, first_player, algorithm_choice):
    computer_move_times = []
    game_graph = GameGraph()
    game_graph.build_graph(stones, player=first_player)
    state = (stones, 0, 0, 0, 0, first_player)
    return game_graph, state, computer_move_times

# -------------- GRAFISKAIS INTERFEISS (Pygame) ----------------
pygame.init()

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AKMEŅU SPĒLE — Pygame versija")
FONT = pygame.font.SysFont(None, 36)

STATE_MENU = 0
STATE_GAME = 1
STATE_GAME_OVER = 2

app_state = STATE_MENU

chosen_stones = 50
chosen_first_player = 1
chosen_algorithm = 1

game_graph = None
state = None
computer_move_times = []

player_can_move = True
start_time_ai = 0.0

result_text = ""
avg_move_time_text = ""

button2_rect = pygame.Rect(30, 440, 220, 50)
button3_rect = pygame.Rect(30, 500, 220, 50)

def draw_text(text, x, y):
    label = FONT.render(text, True, (0, 0, 0))
    SCREEN.blit(label, (x, y))

def draw_button(text, rect):
    pygame.draw.rect(SCREEN, (180, 180, 180), rect)
    label = FONT.render(text, True, (0, 0, 0))
    label_rect = label.get_rect(center=rect.center)
    SCREEN.blit(label, label_rect)

def draw_menu():
    SCREEN.fill((200, 200, 200))
    draw_text("AKMEŅU SPĒLES IZVĒLNE", 250, 50)

    draw_text(f"Pašreizējais akmeņu skaits: {chosen_stones}", 100, 150)
    draw_text("Taustiņi +/− maina akmeņu skaitu (50...70)", 100, 190)

    first_player_text = "Spēlētājs" if chosen_first_player == 1 else "Dators"
    draw_text(f"Kurš sāk pirmais: {first_player_text} (nospied F)", 100, 250)

    algo_text = "Minimax" if chosen_algorithm == 1 else "Alpha-Beta"
    draw_text(f"Algoritms: {algo_text} (nospied A)", 100, 310)

    draw_text("Nospied ENTER, lai sāktu spēli", 100, 370)

def draw_game():
    SCREEN.fill((220, 220, 255))
    draw_text("SPĒLE:", 30, 20)

    if state is None:
        return

    stones_left, p1_s, p2_s, p1_p, p2_p, current_player = state
    final_p1 = p1_s + p1_p
    final_p2 = p2_s + p2_p

    draw_text(f"Atlikuši akmeņi: {stones_left}", 30, 80)

    draw_text(f"Spēlētājs:", 30, 130)
    draw_text(f"  - Paņemtie akmeņi: {p1_s}", 30, 170)
    draw_text(f"  - Punkti: {p1_p}", 30, 210)
    draw_text(f"  - Kopā: {final_p1}", 30, 250)

    draw_text(f"Dators:", 400, 130)
    draw_text(f"  - Paņemtie akmeņi: {p2_s}", 400, 170)
    draw_text(f"  - Punkti: {p2_p}", 400, 210)
    draw_text(f"  - Kopā: {final_p2}", 400, 250)

    turn_text = "Spēlētājs" if current_player == 1 else "Dators"
    draw_text(f"Gājiens: {turn_text}", 30, 320)

    # Рисуем кнопки выбора только если камней >= 3.
    if stones_left >= 3:
        draw_button("Paņemt 2 akmeņus", button2_rect)
        draw_button("Paņemt 3 akmeņus", button3_rect)
    else:
        draw_text("Atlikušis 1 akmenis — notiek automātiska piešķiršana!", 30, 440)

def draw_game_over():
    SCREEN.fill((255, 220, 220))
    draw_text("SPĒLE BEIGUSIES", 300, 50)
    draw_text(result_text, 100, 150)
    draw_text(avg_move_time_text, 100, 200)
    draw_text("Nospied R, lai sāktu no jauna, vai ESC, lai izietu.", 100, 300)

def handle_menu_events(event):
    global chosen_stones, chosen_first_player, chosen_algorithm
    global app_state, game_graph, state, computer_move_times, player_can_move

    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_PLUS, pygame.K_UP, pygame.K_KP_PLUS):
            chosen_stones = min(chosen_stones + 1, 70)
        elif event.key in (pygame.K_MINUS, pygame.K_DOWN, pygame.K_KP_MINUS):
            chosen_stones = max(chosen_stones - 1, 50)

        if event.key == pygame.K_f:
            chosen_first_player = 1 if chosen_first_player == 2 else 2

        if event.key == pygame.K_a:
            chosen_algorithm = 1 if chosen_algorithm == 2 else 2

        if event.key == pygame.K_RETURN:
            game_graph, new_state, times_list = play_game(chosen_stones, chosen_first_player, chosen_algorithm)
            player_can_move = (chosen_first_player == 1)
            global state, computer_move_times
            state = new_state
            computer_move_times = times_list
            app_state = STATE_GAME

def auto_transfer_if_needed():
    """
    Papildnosacījums:
      - Ja uz galda paliek tikai 1 vai 2 akmentiņi, tie automātiski pāriet 
        pašreizējam spēlētājam (kurš veiktu nākamo gājienu),
        un spēle uzreiz beidzas.
      - Ja tie ir 2 akmeņi, punkti tiek pieskaitīti pēc parastajiem noteikumiem.
      - Ja tas ir 1 akmentiņš, spēlētājs saņem +1 punktu.
    Atgriež True, ja tika veikts auto-transfer un spēle beigusies.
    """
    global state
    stones_left, p1_s, p2_s, p1_p, p2_p, current_player = state

    if stones_left == 1:
        # 1 akmentiņš => +1 punktu spēlētājam
        if current_player == 1:
            p1_s += 1
            p1_p += 1
            state = (0, p1_s, p2_s, p1_p, p2_p, 2)
        else:
            p2_s += 1
            p2_p += 1
            state = (0, p1_s, p2_s, p1_p, p2_p, 1)
        finish_game()
        return True

    elif stones_left == 2:
        # 2 akmentiņi => kā parasti: paņemot 2, +2 punkti
        if current_player == 1:
            p1_p += 2
            state = (0, p1_s, p2_s, p1_p, p2_p, 2)
        else:
            p2_p += 2
            state = (0, p1_s, p2_s, p1_p, p2_p, 1)
        finish_game()
        return True

    return False

def handle_game_events(event):
    global state, app_state, computer_move_times
    global start_time_ai, player_can_move

    # Сначала проверяем авто-передачу
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player_can_move:
        if auto_transfer_if_needed():
            # Если камней было 1 или 2, всё уже автоматически распределилось и игра завершилась
            return

        # Если остаётся >=3, обрабатываем нажатие кнопок:
        stones_left = state[0]
        if stones_left >= 3:
            mouse_pos = event.pos
            if button2_rect.collidepoint(mouse_pos):
                make_player_move(2)
            elif button3_rect.collidepoint(mouse_pos):
                make_player_move(3)

def make_player_move(move):
    global state, app_state, player_can_move, computer_move_times, start_time_ai
    stones_left, p1_s, p2_s, p1_p, p2_p, current_player = state

    if move not in [2, 3] or stones_left < move:
        return

    new_stones = stones_left - move
    if new_stones == 0:
        if current_player == 1:
            state = (0, p1_s, p2_s, p1_p + move, p2_p, 2)
        else:
            state = (0, p1_s, p2_s, p1_p, p2_p + move, 1)
    elif new_stones % 2 == 0:
        if current_player == 1:
            state = (new_stones, p1_s + move, p2_s, p1_p, p2_p + 2, 2)
        else:
            state = (new_stones, p1_s, p2_s + move, p1_p + 2, p2_p, 1)
    else:
        if current_player == 1:
            state = (new_stones, p1_s + move, p2_s, p1_p + 2, p2_p, 2)
        else:
            state = (new_stones, p1_s, p2_s + move, p1_p, p2_p + 2, 1)

    if is_game_over(state):
        finish_game()
        return

    player_can_move = False
    start_time_ai = time.time()
    pygame.time.set_timer(pygame.USEREVENT + 1, 100)

def handle_computer_move():
    global state, app_state, computer_move_times, player_can_move

    # Проверяем авто-передачу (1 или 2 камня)
    if auto_transfer_if_needed():
        return

    stones_left, p1_s, p2_s, p1_p, p2_p, current_player = state
    use_alpha_beta = (chosen_algorithm == 2)
    best_state = game_graph.best_move_combined(state, 3, use_alpha_beta)
    if best_state is not None:
        state = best_state

    elapsed_time = time.time() - start_time_ai
    computer_move_times.append(elapsed_time)

    if is_game_over(state):
        finish_game()
    else:
        player_can_move = True

def is_game_over(state_check):
    return (state_check[0] == 0)

def finish_game():
    global app_state, result_text, avg_move_time_text

    final_state = state
    stones_left, p1_s, p2_s, p1_p, p2_p, pl = final_state
    final_p1 = p1_s + p1_p
    final_p2 = p2_s + p2_p

    winner = "Neizšķirts"
    if final_p1 > final_p2:
        winner = "Spēlētājs"
    elif final_p2 > final_p1:
        winner = "Dators"

    result_text = f"Rezultāts: Spēlētājs = {final_p1}, Dators = {final_p2}. Uzvarētājs: {winner}."

    if computer_move_times:
        avg_time = sum(computer_move_times) / len(computer_move_times)
        avg_move_time_text = f"Datora vidējais gājiena laiks: {avg_time:.4f} sek."
    else:
        avg_move_time_text = "Dators neveica gājienus."

    app_state = STATE_GAME_OVER

clock = pygame.time.Clock()

while True:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if app_state == STATE_MENU:
            handle_menu_events(event)
        elif app_state == STATE_GAME:
            if event.type == pygame.USEREVENT + 1:
                handle_computer_move()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            else:
                handle_game_events(event)
        elif app_state == STATE_GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    app_state = STATE_MENU
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    if app_state == STATE_MENU:
        draw_menu()
    elif app_state == STATE_GAME:
        draw_game()
    elif app_state == STATE_GAME_OVER:
        draw_game_over()

    pygame.display.flip()
