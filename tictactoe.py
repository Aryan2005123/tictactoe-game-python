import tkinter as tk
from tkinter import messagebox
import random
import math

BG = "#071021"
CARD = "#000408"
CARD_SHADOW = "#000407"
ACCENT = "#4FD1C5"
SECOND = "#FF8FA3"      
TEXT = "#E6EEF3"
SUBTEXT = "#9FB0BB"
WIN_COLOR = "#FFD166"
GRID_COLOR = "#0EA5A4"
GRID_THICK = 12

FONT_LABEL = ("Consolas", 18, "bold")
FONT_SCORE = ("Consolas", 14, "bold")
FONT_SMALL = ("Consolas", 10)

# Game state

playerX = "X"
playerO = "O"
curr_player = playerX

single_player = True
ai_player = playerO
difficulty = "hard"  # "hard" or "easy"

# board logical state ('', 'X', 'O')
board_state = [[""]*3 for _ in range(3)]
turns = 0
game_over = False

score_X = 0
score_O = 0
score_tie = 0

# AI thinking animation
ai_thinking = False
_think_job = None
_think_dots = 0

# Graphics caches (store ids for drawn items)
cell_highlight_ids = [[None]*3 for _ in range(3)]
mark_ids = [[None]*3 for _ in range(3)]
win_anim_job = None

# ----------------------------
# Tk window (fullscreen)
# ----------------------------
root = tk.Tk()
root.title("Tic Tac Toe — Polished")
root.configure(bg=BG)
root.attributes("-fullscreen", True)
root.resizable(True, True)

def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)
root.bind("<Escape>", exit_fullscreen)

# central area (no big card rectangle — removed to keep background clean)
card_outer = tk.Canvas(root, bg=BG, highlightthickness=0)
card_outer.pack(expand=True, fill="both", padx=20, pady=20)

# inner canvas for board (where grid + marks are drawn)
board_canvas = tk.Canvas(card_outer, bg=CARD, highlightthickness=0)

# Top UI frame (title + score)
top_frame = tk.Frame(root, bg=BG)
top_frame.place(relx=0.5, rely=0.07, anchor="n")

title = tk.Label(top_frame, text="Tic Tac Toe", font=("Consolas", 24, "bold"),
                 bg=BG, fg=TEXT)
title.pack(side="left", padx=(6,18))

score_frame = tk.Frame(top_frame, bg=BG)
score_frame.pack(side="left")
lbl_x = tk.Label(score_frame, text=f"X: {score_X}", font=FONT_SCORE, bg=BG, fg=ACCENT)
lbl_x.pack(side="left", padx=(6,10))
lbl_t = tk.Label(score_frame, text=f"Ties: {score_tie}", font=FONT_SCORE, bg=BG, fg=SUBTEXT)
lbl_t.pack(side="left", padx=(6,10))
lbl_o = tk.Label(score_frame, text=f"O: {score_O}", font=FONT_SCORE, bg=BG, fg=SECOND)
lbl_o.pack(side="left", padx=(6,2))

status = tk.Label(root, text="Your turn", font=FONT_LABEL, bg=BG, fg=TEXT)
status.place(relx=0.5, rely=0.165, anchor="n")

# Controls (Restart, Difficulty, Mode)
ctrl_frame = tk.Frame(root, bg=BG)
ctrl_frame.place(relx=0.5, rely=0.92, anchor="s")

def restart_clicked():
    if game_over:
        play_again = messagebox.askyesno("Play again?", "Start a new game?")
        if not play_again:
            return
    new_game()

restart_btn = tk.Button(ctrl_frame, text="Restart", font=FONT_SMALL, width=12,
                        bg=CARD, fg=TEXT, bd=0, activebackground=CARD_SHADOW,
                        command=restart_clicked)
restart_btn.pack(side="left", padx=6)

def toggle_difficulty():
    global difficulty
    difficulty = "easy" if difficulty == "hard" else "hard"
    diff_btn.configure(text=f"Difficulty: {difficulty.capitalize()}")

diff_btn = tk.Button(ctrl_frame, text=f"Difficulty: {difficulty.capitalize()}", font=FONT_SMALL,
                     width=16, bg=CARD, fg=TEXT, bd=0, activebackground=CARD_SHADOW,
                     command=toggle_difficulty)
diff_btn.pack(side="left", padx=6)

def toggle_mode():
    global single_player, ai_player
    single_player = not single_player
    mode_btn.configure(text="Mode: " + ("1P" if single_player else "2P"))
    ai_player = playerO
    new_game()

mode_btn = tk.Button(ctrl_frame, text="Mode: 1P", font=FONT_SMALL, width=10,
                     bg=CARD, fg=TEXT, bd=0, activebackground=CARD_SHADOW,
                     command=toggle_mode)
mode_btn.pack(side="left", padx=6)

# Footer shortened as requested (only the Esc hint)
footer = tk.Label(root, text="Press Esc to exit fullscreen", font=("Consolas", 9),
                  bg=BG, fg=SUBTEXT)
footer.place(relx=0.98, rely=0.98, anchor="se")


# Layout & responsive drawing

def redraw_layout(event=None):
    # compute central square for board_canvas inside card_outer (centered)
    w = root.winfo_width()
    h = root.winfo_height()

    card_w = int(w * 0.72)
    card_h = int(h * 0.64)
    # board_size centered relative to window (no card rectangle drawn)
    pad = int(min(card_w, card_h) * 0.06)
    board_size = min(card_w - 2*pad, card_h - 2*pad)

    # center board_canvas using relx/rely so it stays centered regardless of sizes/margins
    board_canvas.place(relx=0.5, rely=0.5, anchor="center", width=board_size, height=board_size)

    # redraw contents after canvas has a valid size
    board_canvas.update_idletasks()
    draw_grid_and_marks()

root.bind("<Configure>", redraw_layout)


# Grid, marks, hover, and animations

def draw_grid_and_marks():
    board_canvas.delete("all")
    size = min(board_canvas.winfo_width(), board_canvas.winfo_height())
    if size <= 0:
        return
    # background for the board only (no big card behind)
    board_canvas.create_rectangle(0, 0, size, size, fill="#05141A", outline="")

    cell = size / 3.0
    line_w = max(int(size * 0.02), GRID_THICK)

    # subtle inner border
    board_canvas.create_rectangle(line_w//2, line_w//2, size-line_w//2, size-line_w//2,
                                 outline="#06202A", width=2)

    # grid lines
    for i in (1,2):
        x = i * cell
        board_canvas.create_line(x, 0, x, size, width=line_w, fill=GRID_COLOR, capstyle="round")
        y = i * cell
        board_canvas.create_line(0, y, size, y, width=line_w, fill=GRID_COLOR, capstyle="round")

    # draw existing marks
    for r in range(3):
        for c in range(3):
            draw_mark_in_cell(r, c)

    board_canvas.tag_lower("grid")

def cell_bbox(r, c):
    size = min(board_canvas.winfo_width(), board_canvas.winfo_height())
    cell = size / 3.0
    x0 = c * cell
    y0 = r * cell
    x1 = x0 + cell
    y1 = y0 + cell
    return x0, y0, x1, y1

def draw_mark_in_cell(r, c, animate=False):
    # remove old marks if any
    if mark_ids[r][c]:
        for mid in mark_ids[r][c]:
            try:
                board_canvas.delete(mid)
            except:
                pass
        mark_ids[r][c] = None

    val = board_state[r][c]
    if val == "":
        return

    x0, y0, x1, y1 = cell_bbox(r, c)
    w = x1 - x0
    cx = x0 + w/2
    cy = y0 + w/2

    ids = []
    if val == playerO:
        outer = w*0.38
        inner = w*0.22
        ids.append(board_canvas.create_oval(cx-outer-3, cy-outer+3, cx+outer-3, cy+outer+3, fill="#000000", outline="", stipple="gray50"))
        ring = board_canvas.create_oval(cx-outer, cy-outer, cx+outer, cy+outer, width=int(w*0.065), outline=SECOND)
        ids.append(ring)
        ids.append(board_canvas.create_oval(cx-inner, cy-inner, cx+inner, cy+inner, fill="#05141A", outline=""))
    else:
        size_ = w*0.6
        thickness = max(int(w*0.09), 6)
        x1_ = cx - size_/2; y1_ = cy - size_/2
        x2_ = cx + size_/2; y2_ = cy + size_/2
        x3_ = cx - size_/2; y3_ = cy + size_/2
        x4_ = cx + size_/2; y4_ = cy - size_/2
        ids.append(board_canvas.create_line(x1_+3, y1_+3, x2_+3, y2_+3, width=thickness, capstyle="round", fill="#000000", stipple="gray50"))
        ids.append(board_canvas.create_line(x3_+3, y3_+3, x4_+3, y4_+3, width=thickness, capstyle="round", fill="#000000", stipple="gray50"))
        ids.append(board_canvas.create_line(x1_, y1_, x2_, y2_, width=thickness, capstyle="round", fill=ACCENT))
        ids.append(board_canvas.create_line(x3_, y3_, x4_, y4_, width=thickness, capstyle="round", fill=ACCENT))

    mark_ids[r][c] = ids

    if animate:
        pop_animation(ids, scale_from=0.3, scale_to=1.0, steps=6, delay=18)

def pop_animation(item_ids, scale_from=0.5, scale_to=1.0, steps=6, delay=20):
    def step(i):
        if i > steps:
            return
        if i < steps:
            root.after(delay, lambda: step(i+1))
    step(0)

# Hover handling
hover_rect = None
hover_r, hover_c = -1, -1

def on_mouse_move(event):
    global hover_rect, hover_r, hover_c
    size = min(board_canvas.winfo_width(), board_canvas.winfo_height())
    if size <= 0:
        return
    cell = size / 3.0
    cx = event.x
    cy = event.y
    if cx < 0 or cy < 0 or cx > size or cy > size:
        if hover_rect:
            board_canvas.delete(hover_rect); hover_rect=None
        return
    c = int(cx // cell)
    r = int(cy // cell)
    if r != hover_r or c != hover_c:
        if hover_rect:
            board_canvas.delete(hover_rect)
            hover_rect = None
        hover_r, hover_c = r, c
        if not game_over and not ai_thinking and board_state[r][c] == "":
            x0, y0, x1, y1 = cell_bbox(r, c)
            pad = cell * 0.06
            hover_rect = board_canvas.create_rectangle(x0+pad, y0+pad, x1-pad, y1-pad,
                                                      outline=ACCENT, width=2, dash=(4,6), tags="hover")

board_canvas.bind("<Motion>", on_mouse_move)

def on_click(event):
    global curr_player
    if game_over or ai_thinking:
        return
    size = min(board_canvas.winfo_width(), board_canvas.winfo_height())
    if size <= 0:
        return
    cell = size / 3.0
    cx = event.x; cy = event.y
    if cx < 0 or cy < 0 or cx > size or cy > size:
        return
    c = int(cx // cell); r = int(cy // cell)
    if board_state[r][c] != "":
        return

    place_mark(r, c, curr_player)

    if single_player and (not game_over) and (curr_player == ai_player):
        start_ai_thinking_then_move()

board_canvas.bind("<Button-1>", on_click)

def place_mark(r, c, player, animate=True):
    global turns
    board_state[r][c] = player
    draw_mark_in_cell(r, c, animate=True)
    turns_progress_after_move()


# Game logic & utilities

def update_scoreboard():
    lbl_x.config(text=f"X: {score_X}")
    lbl_o.config(text=f"O: {score_O}")
    lbl_t.config(text=f"Ties: {score_tie}")

def disable_input():
    pass

def enable_input():
    pass

def turns_progress_after_move():
    global turns, curr_player, game_over
    turns += 1
    winner, coords = evaluate_winner()
    if winner is not None:
        if winner == "Tie":
            handle_tie()
        else:
            handle_win(winner, coords)
        return

    curr_player = playerO if curr_player == playerX else playerX

    if single_player:
        if curr_player == playerX:
            status.configure(text="Your turn", fg=TEXT)
        else:
            status.configure(text="AI's turn", fg=SUBTEXT)
    else:
        status.configure(text=f"{curr_player}'s turn", fg=TEXT)

def handle_win(winner_mark, coords):
    global game_over, score_X, score_O, win_anim_job
    stop_ai_thinking()
    game_over = True
    if single_player and winner_mark == ai_player:
        status.configure(text="AI wins!", fg=WIN_COLOR)
    elif single_player and winner_mark == playerX:
        status.configure(text="You win!", fg=WIN_COLOR)
    else:
        status.configure(text=f"{winner_mark} wins!", fg=WIN_COLOR)

    pulse_count = 0
    win_anim_job = None

    def pulse():
        nonlocal pulse_count
        global win_anim_job
        pulse_count += 1
        t = (pulse_count % 2)
        for (r,c) in coords:
            try:
                first_id = mark_ids[r][c][0]
                if board_canvas.type(first_id) == "oval":
                    board_canvas.itemconfigure(first_id, fill=WIN_COLOR if t == 1 else "")
            except Exception:
                pass
        if pulse_count < 8:
            win_anim_job = root.after(220, pulse)
        else:
            for (r,c) in coords:
                x0,y0,x1,y1 = cell_bbox(r,c)
                board_canvas.create_rectangle(x0+4, y0+4, x1-4, y1-4, fill="#FFF3D6", outline="", tags="final")
            if winner_mark == playerX:
                increment_score_X()
            else:
                increment_score_O()
            update_scoreboard()
            root.after(350, ask_play_again)
    pulse()

def handle_tie():
    global game_over, score_tie
    stop_ai_thinking()
    game_over = True
    status.configure(text="Tie!", fg=WIN_COLOR)
    score_tie += 1
    update_scoreboard()
    root.after(350, ask_play_again)

def ask_play_again():
    play = messagebox.askyesno("Play again?", "Do you want to play another round?")
    if play:
        new_game()

def evaluate_winner():
    for r in range(3):
        t0 = board_state[r][0]
        if t0 != "" and t0 == board_state[r][1] == board_state[r][2]:
            return t0, [(r,0),(r,1),(r,2)]
    for c in range(3):
        t0 = board_state[0][c]
        if t0 != "" and t0 == board_state[1][c] == board_state[2][c]:
            return t0, [(0,c),(1,c),(2,c)]
    t0 = board_state[0][0]
    if t0 != "" and t0 == board_state[1][1] == board_state[2][2]:
        return t0, [(0,0),(1,1),(2,2)]
    t0 = board_state[0][2]
    if t0 != "" and t0 == board_state[1][1] == board_state[2][0]:
        return t0, [(0,2),(1,1),(2,0)]
    if all(board_state[r][c] != "" for r in range(3) for c in range(3)):
        return "Tie", None
    return None, None

def increment_score_X():
    global score_X
    score_X += 1

def increment_score_O():
    global score_O
    score_O += 1


# AI thinking animation helpers

def start_ai_thinking():
    global ai_thinking, _think_job, _think_dots
    stop_ai_thinking()
    ai_thinking = True
    _think_dots = 0
    disable_input()
    status.configure(text="AI is thinking", fg=SUBTEXT)
    _think_job = root.after(280, _ai_thinking_tick)

def _ai_thinking_tick():
    global _think_dots, _think_job
    if not ai_thinking:
        return
    _think_dots = (_think_dots + 1) % 4
    dots = "." * _think_dots
    status.configure(text=f"AI is thinking{dots}", fg=SUBTEXT)
    _think_job = root.after(280, _ai_thinking_tick)

def stop_ai_thinking():
    global ai_thinking, _think_job, _think_dots
    if _think_job is not None:
        try:
            root.after_cancel(_think_job)
        except:
            pass
    _think_job = None
    ai_thinking = False
    _think_dots = 0
    enable_input()

def start_ai_thinking_then_move(min_delay=600):
    start_ai_thinking()
    root.after(min_delay, _perform_ai_move_and_stop_thinking)

def _perform_ai_move_and_stop_thinking():
    stop_ai_thinking()
    ai_move()


# AI (Minimax for hard)

def ai_move():
    global curr_player
    if game_over:
        return
    if not single_player or curr_player != ai_player:
        return

    if difficulty == "easy":
        empties = [(r,c) for r in range(3) for c in range(3) if board_state[r][c] == ""]
        if empties:
            r,c = random.choice(empties)
            place_mark(r, c, ai_player)
        return

    best_score = None; best_move = None
    for r in range(3):
        for c in range(3):
            if board_state[r][c] == "":
                board_state[r][c] = ai_player
                score = minimax(0, False)
                board_state[r][c] = ""
                if best_score is None or score > best_score:
                    best_score = score
                    best_move = (r,c)
    if best_move:
        r,c = best_move
        place_mark(r, c, ai_player)

def minimax(depth, is_maximizing):
    result, _ = evaluate_winner()
    if result is not None:
        if result == ai_player:
            return 1
        elif result == "Tie":
            return 0
        else:
            return -1
    if is_maximizing:
        best = -999
        for r in range(3):
            for c in range(3):
                if board_state[r][c] == "":
                    board_state[r][c] = ai_player
                    score = minimax(depth+1, False)
                    board_state[r][c] = ""
                    best = max(best, score)
        return best
    else:
        best = 999
        for r in range(3):
            for c in range(3):
                if board_state[r][c] == "":
                    board_state[r][c] = playerX
                    score = minimax(depth+1, True)
                    board_state[r][c] = ""
                    best = min(best, score)
        return best

# Reset / New game

def new_game():
    global turns, game_over, curr_player, mark_ids, board_state, win_anim_job
    stop_ai_thinking()
    if win_anim_job:
        try:
            root.after_cancel(win_anim_job)
        except:
            pass
    turns = 0
    game_over = False
    curr_player = playerX
    board_state = [[""]*3 for _ in range(3)]
    for r in range(3):
        for c in range(3):
            if mark_ids[r][c]:
                for iid in mark_ids[r][c]:
                    try: board_canvas.delete(iid)
                    except: pass
                mark_ids[r][c] = None
    if single_player:
        status.configure(text="Your turn", fg=TEXT)
    else:
        status.configure(text=f"{curr_player}'s turn", fg=TEXT)
    draw_grid_and_marks()
    update_scoreboard()


root.update_idletasks()
redraw_layout()
new_game()


root.mainloop()
