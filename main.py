import tkinter as tk
from tkinter import ttk
import time
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
        """
        Novērtējuma funkcija:
        state: (akmeni_atlika, sp1_akmeni, sp2_akmeni, sp1_punkti, sp2_punkti, kam_gajiens)
        """
        akmeni_atlika, sp1_akm, sp2_akm, sp1_punkti, sp2_punkti, kam_gajiens = state
        return (sp2_punkti - sp1_punkti) + (sp2_akm - sp1_akm) + \
               (2 if akmeni_atlika > 0 and akmeni_atlika % 2 == (0 if kam_gajiens == 1 else 1) else 0)

    def build_graph(self, stones, sp1_akm=0, sp2_akm=0, sp1_punkti=0, sp2_punkti=0, speletajs=1):
        """
        Veido stāvokļu grafu platumā, sākot no dotā akmeņu skaita.
        """
        queue = deque()
        sakuma_stavoklis = (stones, sp1_akm, sp2_akm, sp1_punkti, sp2_punkti, speletajs)
        queue.append(sakuma_stavoklis)
        self.explored.add(sakuma_stavoklis)
        self.add_node(sakuma_stavoklis)

        while queue:
            current_state = queue.popleft()
            akmeni_atlika, sp1_akm, sp2_akm, sp1_punkti, sp2_punkti, kam_gajiens = current_state

            if akmeni_atlika == 0:
                continue

            for cik_panak in [2, 3]:
                if akmeni_atlika >= cik_panak:
                    jaunais_atlika = akmeni_atlika - cik_panak
                    if jaunais_atlika == 0:
                        if kam_gajiens == 1:
                            jaunais_stavoklis = (jaunais_atlika, sp1_akm, sp2_akm, sp1_punkti + cik_panak, sp2_punkti, 2)
                        else:
                            jaunais_stavoklis = (jaunais_atlika, sp1_akm, sp2_akm, sp1_punkti, sp2_punkti + cik_panak, 1)
                    else:
                        if jaunais_atlika % 2 == 0:
                            if kam_gajiens == 1:
                                jaunais_stavoklis = (jaunais_atlika, sp1_akm + cik_panak, sp2_akm, sp1_punkti, sp2_punkti + 2, 2)
                            else:
                                jaunais_stavoklis = (jaunais_atlika, sp1_akm, sp2_akm + cik_panak, sp1_punkti + 2, sp2_punkti, 1)
                        else:
                            if kam_gajiens == 1:
                                jaunais_stavoklis = (jaunais_atlika, sp1_akm + cik_panak, sp2_akm, sp1_punkti + 2, sp2_punkti, 2)
                            else:
                                jaunais_stavoklis = (jaunais_atlika, sp1_akm, sp2_akm + cik_panak, sp1_punkti, sp2_punkti + 2, 1)

                    self.add_node(jaunais_stavoklis)
                    self.add_edge(current_state, jaunais_stavoklis)

                    if jaunais_stavoklis not in self.explored:
                        queue.append(jaunais_stavoklis)
                        self.explored.add(jaunais_stavoklis)

    def minimax(self, state, depth, max_depth, maximizing_player, cache):
        """
        Parastais Minimax (dziļums depth līdz max_depth).
        """
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
        """
        Minimax ar alfa-bēta atgriezumiem.
        """
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
        """
        Izvēlas labāko nākamo gājienu (Minimax vai Alfa-bēta).
        Atgriež child-state, kas vislabāk izdevīgs esošajam spēlētājam.
        """
        children = self.graph.get(state, [])
        if not children:
            return None

        maximizing_player = (state[5] == 2)
        if maximizing_player:
            best_val = float('-inf')
        else:
            best_val = float('inf')

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
            elif not maximizing_player and val < best_val:
                best_val = val
                best_child = child

        return best_child


class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Akmens spēle (2 vai 3)")

        self.stones = 50
        self.first_player = 1
        self.algorithm_choice = 1

        self.game_graph = None
        self.state = None
        self.computer_move_times = []   

        self.create_widgets()

    def create_widgets(self):
        frame_options = ttk.LabelFrame(self, text="Spēles iestatījumi")
        frame_options.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(frame_options, text="Sākuma akmeņu skaits (50-70):").pack(anchor=tk.W)
        self.spin_stones = tk.Spinbox(
            frame_options, from_=50, to=70, width=5
        )
        self.spin_stones.pack(anchor=tk.W, pady=2)

        ttk.Label(frame_options, text="Kurš sāk spēli?").pack(anchor=tk.W)
        self.first_player_var = tk.IntVar(value=1)
        rb_player1 = ttk.Radiobutton(frame_options, text="Jūs (Spēlētājs)", variable=self.first_player_var, value=1)
        rb_player2 = ttk.Radiobutton(frame_options, text="Dators", variable=self.first_player_var, value=2)
        rb_player1.pack(anchor=tk.W)
        rb_player2.pack(anchor=tk.W)

        ttk.Label(frame_options, text="Izvēlieties datora algoritmu:").pack(anchor=tk.W)
        self.algorithm_var = tk.IntVar(value=1)
        rb_minimax = ttk.Radiobutton(frame_options, text="Minimax", variable=self.algorithm_var, value=1)
        rb_alphabeta = ttk.Radiobutton(frame_options, text="Alfa-bēta", variable=self.algorithm_var, value=2)
        rb_minimax.pack(anchor=tk.W)
        rb_alphabeta.pack(anchor=tk.W)

        self.start_button = ttk.Button(frame_options, text="Sākt spēli", command=self.start_game)
        self.start_button.pack(pady=5)

        frame_game = ttk.LabelFrame(self, text="Spēles gaita")
        frame_game.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.game_state_text = tk.Text(frame_game, height=10, width=60, state='disabled')
        self.game_state_text.pack(pady=5)

        self.player_move_var = tk.StringVar()
        ttk.Label(frame_game, text="Jūsu gājiens (2 vai 3):").pack(anchor=tk.W)
        self.entry_move = ttk.Entry(frame_game, textvariable=self.player_move_var, width=5)
        self.entry_move.pack(anchor=tk.W, pady=2)

        self.move_button = ttk.Button(frame_game, text="Veikt gājienu", command=self.player_move)
        self.move_button.pack(pady=5)

        self.restart_button = ttk.Button(frame_game, text="Sākt no jauna", command=self.restart_game)
        self.restart_button.pack(pady=5)
        self.restart_button.config(state='disabled')

    def start_game(self):
        """
        Inicializē jaunu spēli saskaņā ar iestatījumiem.
        """
        self.stones = int(self.spin_stones.get())
        self.first_player = self.first_player_var.get()
        self.algorithm_choice = self.algorithm_var.get()

        self.game_graph = GameGraph()
        self.game_graph.build_graph(self.stones, speletajs=self.first_player)

        self.state = (self.stones, 0, 0, 0, 0, self.first_player)
        self.computer_move_times = []

        self.clear_game_text()
        self.append_game_text(f"Sākam jaunu spēli!\n"
                              f"Akmeņu skaits uz galda: {self.stones}\n"
                              f"Pirmais gājiens: {'Jūs' if self.first_player == 1 else 'Dators'}\n"
                              f"Algoritms: {'Minimax' if self.algorithm_choice == 1 else 'Alfa-bēta'}\n")

        if self.first_player == 2:
            self.computer_turn()

    def player_move(self):
        """
        Spēlētāja (1) gājiens. Nolasa ievadīto akmeņu skaitu, pārbauda derīgumu,
        veic izmaiņas stāvoklī un, ja spēle nav galā, ļauj datoram iet.
        """
        if self.state is None or self.state[0] == 0:
            return  # Spēle jau beigusies vai nav sākta

        kam_gajiens = self.state[5]
        if kam_gajiens != 1:
            self.append_game_text("Tagad nav jūsu gājiens!\n")
            return

        try:
            cik_panak = int(self.player_move_var.get())
        except ValueError:
            self.append_game_text("Lūdzu ievadiet 2 vai 3.\n")
            return

        if cik_panak not in [2, 3]:
            self.append_game_text("Nederīgs gājiens! Var paņemt tikai 2 vai 3 akmeņus.\n")
            return

        if self.state[0] < cik_panak:
            self.append_game_text("Nav iespējams paņemt vairāk akmeņu, nekā atlicis!\n")
            return

        jaunais_atlika = self.state[0] - cik_panak
        sp1_akm, sp2_akm, sp1_punkti, sp2_punkti = self.state[1], self.state[2], self.state[3], self.state[4]

        if jaunais_atlika == 0:
            sp1_punkti += cik_panak
            nakamais = 2
        else:
            if jaunais_atlika % 2 == 0:
                sp1_akm += cik_panak
                sp2_punkti += 2
                nakamais = 2
            else:
                sp1_akm += cik_panak
                sp1_punkti += 2
                nakamais = 2

        self.state = (jaunais_atlika, sp1_akm, sp2_akm, sp1_punkti, sp2_punkti, nakamais)
        self.update_game_state_text()

        if self.apply_one_stone_rule_if_needed():
            return

        if self.check_game_over():
            return

        self.computer_turn()

    def computer_turn(self):
        """
        Datora (2) gājiens. Izsauc best_move_combined un mēra laiku.
        """
        if self.state is None or self.state[0] == 0:
            return

        kam_gajiens = self.state[5]
        if kam_gajiens != 2:
            return

        start_time = time.time()
        use_alpha_beta = (self.algorithm_choice == 2)
        next_state = self.game_graph.best_move_combined(self.state, 3, use_alpha_beta)
        end_time = time.time()

        elapsed = end_time - start_time
        self.computer_move_times.append(elapsed)

        if next_state is not None:
            self.state = next_state
            self.append_game_text(f"Dators izdarīja gājienu ({elapsed:.4f} s).\n")
        else:
            self.append_game_text("Dators nevar izdarīt gājienu.\n")

        self.update_game_state_text()

        if self.apply_one_stone_rule_if_needed():
            return

        self.check_game_over()

    def apply_one_stone_rule_if_needed(self):
        """
        Ja paliek precīzi 1 akmens, tas automātiski pāriet pretiniekam (tam, kurš NAV gājienu darījis),
        un spēle beidzas (akmeņi uz galda kļūst 0).
        """
        if self.state and self.state[0] == 1:
            akm, sp1_akm, sp2_akm, sp1_punkti, sp2_punkti, kam_gajiens = self.state

            if kam_gajiens == 1:
                sp2_akm += 1
                self.append_game_text("\nPēc jūsu gājiena palika 1 akmens, tas pāriet datoram un spēle beidzas!\n")
            else:
                sp1_akm += 1
                self.append_game_text("\nPēc datora gājiena palika 1 akmens, tas pāriet jums un spēle beidzas!\n")

            self.state = (0, sp1_akm, sp2_akm, sp1_punkti, sp2_punkti, kam_gajiens)
            self.update_game_state_text()
            self.check_game_over()
            return True

        return False

    def check_game_over(self):
        """
        Pārbaudām, vai spēle beigusies (akmeņu nav).
        Ja jā – izvadām rezultātu un ieslēdzam pogu "Sākt no jauna".
        """
        if self.state and self.state[0] == 0:
            akm, sp1_akm, sp2_akm, sp1_punkti, sp2_punkti, pl = self.state
            gala_sp1 = sp1_akm + sp1_punkti
            gala_sp2 = sp2_akm + sp2_punkti

            self.append_game_text("\n--- Spēle ir galā! ---\n")
            self.append_game_text(f"Jūsu kopsumma: {gala_sp1}\nDatora kopsumma: {gala_sp2}\n")

            if gala_sp1 > gala_sp2:
                self.append_game_text("Jūs uzvarējāt!\n")
            elif gala_sp2 > gala_sp1:
                self.append_game_text("Dators uzvarēja!\n")
            else:
                self.append_game_text("Neizšķirts!\n")

            if self.computer_move_times:
                vid_laiks = sum(self.computer_move_times) / len(self.computer_move_times)
                self.append_game_text(f"Datora vidējais gājiena laiks: {vid_laiks:.4f} s.\n")

            self.restart_button.config(state='normal')
            return True
        return False

    def restart_game(self):
        """
        Sāk visu no jauna (spēli var uzsākt atkārtoti).
        """
        self.state = None
        self.computer_move_times.clear()
        self.clear_game_text()
        self.append_game_text("Iestatījumi atiestatīti. Lūdzu ievadiet jaunus un spiediet 'Sākt spēli'.\n")
        self.restart_button.config(state='disabled')

    def update_game_state_text(self):
        """
        Atjauno stāvokļa info teksta laukā.
        """
        akm, sp1_akm, sp2_akm, sp1_punkti, sp2_punkti, kam_gajiens = self.state
        self.append_game_text(
            f"\nPašreizējais stāvoklis:\n"
            f"Atlikušo akmeņu skaits: {akm}\n"
            f"Jums rokās: {sp1_akm} | Jūsu punkti: {sp1_punkti}\n"
            f"Datoram rokās: {sp2_akm} | Datora punkti: {sp2_punkti}\n"
            f"Gājiens: {'Jūs' if kam_gajiens == 1 else 'Dators'}\n"
        )

    def clear_game_text(self):
        self.game_state_text.config(state='normal')
        self.game_state_text.delete(1.0, tk.END)
        self.game_state_text.config(state='disabled')

    def append_game_text(self, text):
        self.game_state_text.config(state='normal')
        self.game_state_text.insert(tk.END, text)
        self.game_state_text.see(tk.END)
        self.game_state_text.config(state='disabled')


if __name__ == "__main__":
    app = GameApp()
    app.mainloop()