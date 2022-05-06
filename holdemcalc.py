from Card import Card
from functools import partial
import subprocess
import re
import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog
from PIL import Image, ImageTk


# Functions -------------------------------------------------------------------
def cancel_card(*args, h_win):
  h_win.destroy()

def submit_card(*args, h_win, player, card_pos):
  global g_cards
  current_card_index = 2 * player + card_pos - 1 if player != -1 else 2 * 9 + card_pos - 1
  # Update the cards list with the last toggled card state
  g_cards[current_card_index] = g_card_toggle
  # Change players card image in main GUI to the new card
  if player == -1:
    label_handle = f"h_com_c{card_pos}_lbl"
  else:
    label_handle = f"h_p{player}_c{card_pos}_lbl"
  exec(f"{label_handle}['image'] = c{g_card_toggle}_img")
  h_win.destroy()

def toggle_card(*args, card, player, card_pos, card_handles):
  global g_card_toggle
  if card == g_card_toggle:
    # They unselcted their card, change background and update g_card_toggle
    exec(f"card_handles[{card}]['background'] = '#ffffff'")
    g_card_toggle = 52
  else:
    # They picked a new card, if their previous card wasn't random,
    # unselect it and then select the new card
    if g_card_toggle != 52:
      exec(f"card_handles[{g_card_toggle}]['background'] = '#ffffff'")
    # Select the new card by highlighting it and setting g_card_toggle
    exec(f"card_handles[{card}]['background'] = '#33ff33'")
    g_card_toggle = card

def choose_card(*args, player, card_pos):
  global g_cards, g_card_toggle
  current_card_index = 2 * player + card_pos - 1 if player != -1 else 2 * 9 + card_pos - 1
  g_card_toggle = g_cards[current_card_index]
  chosen_cards = g_cards[:]
  del chosen_cards[current_card_index]
  card_xspace = 70
  card_yspace = 95
  win_width = card_xspace * 13
  win_height = card_yspace * 4 + 60
  # Create popup winddow
  popup = Toplevel(h_root)
  popup.geometry(f"{win_width}x{win_height}")
  popup.geometry(f"+{h_root.winfo_rootx()+main_window_width//2-win_width//2}"
                 f"+{h_root.winfo_rooty()+main_window_height//2-win_height//2}")
  # Create card labels and bind click callback to them
  card_handles = []
  for card in range(52):
    exec(f"h_c{card}_lbl = ttk.Label(popup,image=c{card}_img, padding='5 5 5 5', relief='groove')")
    eval(f"card_handles.append(h_c{card}_lbl)")
    eval(f"h_c{card}_lbl.place(x={(card%13)*card_xspace}, y={(card//13)*card_yspace})")
    # If card selected in main GUI is one of the 52, then highlight it in picker window
    if card == g_card_toggle:
      exec(f"h_c{card}_lbl['background'] = '#33ff33'")
    # If card is in chosen_card list then remove its image and unbind the callback, else bind callback
    if card in chosen_cards:
      eval(f"h_c{card}_lbl.unbind('<Button-1>')")
      exec(f"h_c{card}_lbl['image'] = cNone_img")
    else:
      eval(f"h_c{card}_lbl.bind('<Button-1>', partial(toggle_card,card={card}, "
           f"player=player, card_pos=card_pos, card_handles=card_handles))")
  # Create submit and cancel buttons
  ttk.Button(popup, text="Submit", padding="6 6 6 6", \
    command=partial(submit_card, h_win=popup, player=player, card_pos=card_pos)).place(x=win_width//2-100,y=win_height-50)
  ttk.Button(popup, text="Cancel", padding="6 6 6 6", \
    command=partial(cancel_card, h_win=popup)).place(x=win_width//2-0,y=win_height-50)
  # Block main window callbacks until popup is closed
  popup.grab_set()

def update_num_opp(*args):
  global g_cards
  no = int(num_opp.get())
  # Show all players up to num_opp
  for player in range(no + 1):
    exec(f"h_p{player}_label.place(x=p{player}_start[0], y=p{player}_start[1])")
    exec(f"h_p{player}_c1_lbl.place(x=p{player}_start[0], y=p{player}_start[1] + card_y_lbl_offset)")
    exec(f"h_p{player}_c2_lbl.place(x=p{player}_start[0] + card_x_offset, y=p{player}_start[1] + card_y_lbl_offset)")
  # Hide all players above num_opp and and set their cards to random
  for player in range(no + 1, 9):
    # Hide player label
    exec(f"h_p{player}_label.place_forget()")
    # Hide player cards and return to deck if necessary
    for card_pos in range(1, 3):
      # Hide card label and change image to random
      exec(f"h_p{player}_c{card_pos}_lbl.place_forget()")
      exec(f"h_p{player}_c{card_pos}_lbl['image'] = c52_img")
      # Make card random since no longer in game
      g_cards[2 * player + card_pos - 1] = 52

def check_num_trials(*args):
  entry = num_trials.get()
  if len(entry) !=0 and not num_trials.get().isnumeric():
    messagebox.showerror(title="Bad Input", message="# of Trials must be a positive integer.")
    num_trials.set(value=5000)
  elif len(entry) !=0 and int(entry) > num_trials_max:
    num_trials.set(value=num_trials_max)

def clear_all_cards(*args):
  global g_cards
  num_players = int(num_opp.get()) + 1
  # Clear fixed cards for players
  for player in range(num_players):
    for card_pos in range(1, 3):
      # Set card to random
      g_cards[2 * player + card_pos - 1] = 52
      # Set card label image to random
      exec(f"h_p{player}_c{card_pos}_lbl['image'] = c52_img")
  # Clear fixed cards for community cards
  for card_pos in range(1, 6):
    # Set card to random
    g_cards[2 * 9 + card_pos - 1] = 52
    # Set card label image to random
    exec(f"h_com_c{card_pos}_lbl['image'] = c52_img")

def is_valid_fname(fname):
  if re.search(r'[^A-Za-z0-9_ \-\\]', fname):
    messagebox.showerror(title="Error", message="Illegal Filename!")
    return False
  else:
    return True

def run_save(*args):
  sim_config = dict()
  get_simulation_setup(sim_config)
  # Get filename
  while True:
    fname = simpledialog.askstring("Filename", "Please enter a filename to save")
    if fname is None:
      return
    elif is_valid_fname(fname):
      break
  # Write info to output file
  if not os.path.isdir("./Save"):
    os.mkdir("./Save")
  fh = open('./Save/' + fname + '.sim', 'w')
  fh.write(f"{sim_config['num_runs']} {sim_config['num_opponents']} {sim_config['calc_percentages']}\n")
  for player in range(sim_config['num_opponents'] + 1):
    fh.write(f"{g_cards[2 * player]} {g_cards[2 * player + 1]}\n")
  fh.write(f"{' '.join([str(e) for e in g_cards[18:23]])}\n")
  fh.close()

def run_load(*args):
  global g_cards
  sim_config = dict()
  # Choose file to load
  fname = filedialog.askopenfilename(initialdir=os.getcwd() + '/Save', filetypes=[("Sim Files", "*.sim")])
  if len(fname) == 0:
    return
  fh = open(fname, 'r')
  # Extract first line
  num_runs, num_opponents, calc_percentages = fh.readline().strip().split()
  # Extract player cards
  for player in range(int(num_opponents) + 1):
    cards =  fh.readline().strip().split()
    g_cards[2 * player] = int(cards[0])
    g_cards[2 * player + 1] = int(cards[1])
  # Extract community cards
  cards =  fh.readline().strip().split()
  g_cards[2 * 9] = int(cards[0])
  g_cards[2 * 9 + 1] = int(cards[1])
  g_cards[2 * 9 + 2] = int(cards[2])
  g_cards[2 * 9 + 3] = int(cards[3])
  g_cards[2 * 9 + 4] = int(cards[4])
  fh.close()
  # Set option GUI variables
  num_trials.set(num_runs)
  num_opp.set(num_opponents)
  win_pct.set("------")
  tie_pct.set("------")
  lose_pct.set("------")
  plot_pct_history.set(calc_percentages)
  # Clear unused players
  update_num_opp()
  # Load each players card images
  for player in range(int(num_opponents) + 1):
    for card_pos in range(1,3):
      card = g_cards[2 * player + card_pos - 1]
      # Set card image
      exec(f"h_p{player}_c{card_pos}_lbl['image'] = c{card}_img")
  # Load community card images
  for card_pos in range(1,6):
    card = g_cards[2 * 9 + card_pos - 1]
    # Set card image
    exec(f"h_com_c{card_pos}_lbl['image'] = c{card}_img")

def run_report(*args):
  pass

def get_simulation_setup(sim_config):
  num_runs = num_trials.get()
  if len(num_runs) ==0:
    num_runs = 5000
  else:
    num_runs = int(num_runs)
  num_opponents = int(num_opp.get())
  calc_percentages = int(plot_pct_history.get())
  sim_config['num_runs'] = num_runs
  sim_config['num_opponents'] = num_opponents
  sim_config['calc_percentages'] = calc_percentages

def run_simulation(*args):
  global g_cards
  # Check all simulation parameters
  num_runs = num_trials.get()
  if len(num_runs) ==0:
    messagebox.showerror(title="Bad Input", message="# of Trials cannot be empty.")
    return
  else:
    num_runs = int(num_runs)
  # Create simulation structure dictionary
  sim_config = dict()
  get_simulation_setup(sim_config)
  # Write info to input file
  fh = open(calculator_input_fname, 'w')
  fh.write(f"{num_runs} {sim_config['num_opponents'] + 1} {sim_config['calc_percentages']}\n")
  for player in range(sim_config['num_opponents'] + 1):
    fh.write(f"{g_cards[2 * player]} {g_cards[2 * player + 1]}\n")
  fh.write(f"{' '.join([str(e) for e in g_cards[18:23]])}\n")
  fh.close()
  # Popup Calulating message
  popup = Toplevel(h_root)
  popup.geometry("170x70")
  popup.geometry(f"+{h_root.winfo_rootx()+main_window_width//2}+{h_root.winfo_rooty()+main_window_height//2}")
  ttk.Label(popup, text="calculating...", padding="10 10 10 10", anchor="center", background="#33ff33", \
  font=("Arial",16)).place(x=16, y=12)
  popup.update()
  # Run Calculator
  subprocess.run("Calculator")
  # Close pop-up
  popup.destroy()
  # Read in results & populate GUI
  fh = open(calculator_results_fname, 'r')
  results = [line.strip() for line in fh]
  fh.close()
  win_pct.set(f"{float(results[0]) * 100:.2f}")
  tie_pct.set(f"{float(results[1]) * 100:.2f}")
  lose_pct.set(f"{float(results[2]) * 100:.2f}")
  if plot_pct_history.get() == '1':
    dtype = np.dtype('f4')
    with open(calculator_percent_fname, 'rb') as f:
      pct_data = 100 * np.fromfile(f, dtype)
    f.close()
    x_data = np.linspace(1, num_runs, num_runs).astype(int)
    win_pct_data  = pct_data[0:num_runs]
    tie_pct_data  = pct_data[num_runs:2 * num_runs]
    loss_pct_data = pct_data[2 * num_runs:3 * num_runs]
    fig = plt.figure(1)
    plt.clf()
    plt.plot(x_data, win_pct_data, 'g', label="Win %")
    plt.plot(x_data, loss_pct_data, 'r', label="Loss %")
    plt.plot(x_data, tie_pct_data, 'b', label="Tie %")
    plt.legend(loc="upper right")
    # if num_runs > 100000:
    #   plt.xscale('log')
    plt.axis([1, num_runs, 0, 100])
    plt.grid(visible=True)
    title_str = f"{num_runs} Trials for ({CARD_INT_TO_STR[g_cards[0]]}, "\
                f"{CARD_INT_TO_STR[g_cards[1]]}) vs {sim_config['num_opponents']} "\
                f"opponent{'s' if sim_config['num_opponents'] > 1 else ''}\n Opponent's Hands: "
    for player in range(1, sim_config['num_opponents'] + 1):
      card1 = CARD_INT_TO_STR[g_cards[2 * player]]
      card2 = CARD_INT_TO_STR[g_cards[2 * player + 1]]
      if player == sim_config['num_opponents']:
        title_str += f"({card1}, {card2})"
      else:
        title_str += f"({card1}, {card2}), "
    bcrds = [CARD_INT_TO_STR[e] for e in g_cards[18:23]]
    title_str += f"\nBoard Cards= ({bcrds[0]}, {bcrds[1]}, {bcrds[2]}, {bcrds[3]}, {bcrds[4]})"
    plt.title(label=title_str, fontsize=10)
    plt.show(block = False)
    fig.canvas.draw()
    fig.canvas.flush_events()
  # Save simulation in history list for report






  #DEBUG
  if DEBUG:
    print(f"\nSim Config:")
    print(f"\t# of runs = {num_runs}")
    print(f"\t# of opponents = {sim_config['num_opponents']}")
    print(f"\tDo Percentages = {sim_config['do_percentages']}")
    for player in range(sim_config['num_opponents'] + 1):
      g_cards = eval(f"sim_config['p{player}_cards']")
      print(f"\tPlayer #{player} cards = ({cards[0]}, {cards[1]})")
    cards = sim_config['com_cards']
    print(f"\tCommunity cards = ({cards[0]}, {cards[1]},  {cards[2]}, {cards[3]}, {cards[4]})")
  #DEBUG
#------------------------------------------------------------------------------


# Global variables ------------------------------------------------------------
DEBUG = 0
CARD_INT_TO_STR = {
                    0: ' 2C',  1: '3C',  2: '4C',  3: '5C',  4: '6C',  5: '7C',
                    6: '8C',  7: '9C',  8: '10C',  9: 'JC', 10: 'QC', 11: 'KC', 12: 'AC',
                    13: '2D', 14: '3D', 15: '4D', 16: '5D', 17: '6D', 18: '7D',
                    19: '8D', 20: '9D', 21: '10D', 22: 'JD', 23: 'QD', 24: 'KD', 25: 'AD',
                    26: '2H', 27: '3H', 28: '4H', 29: '5H', 30: '6H', 31: '7H',
                    32: '8H', 33: '9H', 34: '10H', 35: 'JH', 36: 'QH', 37: 'KH', 38: 'AH',
                    39: '2S', 40: '3S', 41: '4S', 42: '5S', 43: '6S', 44: '7S',
                    45: '8S', 46: '9S', 47: '10S', 48: 'JS', 49: 'QS', 50: 'KS', 51: 'AS', 52: '?'
                  }
calculator_input_fname = "input.txt"
calculator_results_fname = "calcResults.txt"
calculator_percent_fname = "calcPercents.dat"
calculator_service_fname = "calcService.txt"
sim_service_fname = "holdem_service.txt"
com_player_num = -1
initial_num_opp = 1
num_trials_init = 5000
num_trials_max = 10000000
# Non-constants
g_cards = [52] * 23
g_card_toggle = 52
g_simulation_history = []
# -----------------------------------------------------------------------------

# GUI Settings ----------------------------------------------------------------
main_title = "Hold'em Odds"
main_window_width = 890
main_window_height = 540
board_window_width = 880
root_frame_padding = "5 5 5 5"
label_relief_default = 'ridge'
label_padding_default = "5 5 5 5"
player_label_width = 20
player_label_color = "#c0c0c0"
user_label_color = "#66ff66"
option_label_color = "#ffff66"
results_label_color = "#66ff66"
trials_label_width = 12
results_label_width = 10
community_label_width = 56
card_width = 57
card_height = 80
card_padding_default = "2 2 2 2"
num_opp_label_width = 15
btn_width_default = 10
cards_relief = "groove"
result_relief = "sunken"
card_y_lbl_offset = 30
card_x_offset = 70
card_y_card_offset = card_y_lbl_offset + 24
card_y_cb_offset = card_y_card_offset + 22
p6_start = (80, 75)
p7_start = (p6_start[0] - 40, p6_start[1] + 135)
p8_start = (p7_start[0] + 152 + 12, p7_start[1] + 70)
p0_start = (p8_start[0] + 152 + 15, p8_start[1])
p1_start = (p0_start[0] + 152 + 15, p8_start[1])
p2_start = (p1_start[0] + 152 + 12, p1_start[1] - 70)
p3_start = (p2_start[0] - 40, p2_start[1] - 135)
p5_start = (p6_start[0] + 152 + 40, p6_start[1] - 55)
p4_start = (p3_start[0] - 152 - 40, p5_start[1])
com_start = (p6_start[0] + 152 + 30, p3_start[1] + 75)
results_start = (p0_start[0], p0_start[1] + 142)
result_y_space = 35
results_x_space = 80
trials_start = (10, results_start[1] + 45)
num_opp_start = (trials_start[0] + 95, trials_start[1])
num_opp_x_space = 50
frame_space = 5
cards_frame_start = (board_window_width + frame_space, 0)
btn_x_space = 75
btn_start = (results_start[0] + results_x_space + 130, results_start[1] + 2 * result_y_space)
clear_cards_start = (num_opp_start[0] + 115, trials_start[1] + 32)
# -----------------------------------------------------------------------------


# GUI Definition --------------------------------------------------------------
h_root = Tk()
h_root.title(main_title)
h_root.geometry(f"{main_window_width}x{main_window_height}")
h_root.resizable(False, False)
h_root_frame = ttk.Frame(h_root, padding = root_frame_padding, width=main_window_width, height=main_window_height)
h_board_frame = ttk.Frame(h_root_frame, width=board_window_width, height=main_window_height-130, relief="groove")

# Load card images
for card in range(53):
  fname = os.getcwd() + "\\CARDS\\" + f"{card}.png"
  exec(f"c{card}_img = Image.open(fname)")
  exec(f"c{card}_img = c{card}_img.resize(({card_width}, {card_height}), Image.Resampling.LANCZOS)")
  exec(f"c{card}_img = ImageTk.PhotoImage(c{card}_img)")
cNone_img = Image.open(".\\CARDS\\None.jpg")
cNone_img = eval(f"cNone_img.resize(({card_width}, {card_height}), Image.Resampling.LANCZOS)")
cNone_img = ImageTk.PhotoImage(cNone_img)

num_trials = StringVar(value=f"{num_trials_init}")
num_trials.trace_add("write", check_num_trials)
num_opp = StringVar(value=initial_num_opp)
win_pct = StringVar(value="------")
tie_pct = StringVar(value="------")
lose_pct = StringVar(value="------")
plot_pct_history = StringVar(value=1)

# Player card widgets
for player in range(9):
  # Player label
  if player == 0:
    player_label_str = "Your Cards"
    bg_color = user_label_color
  else:
    player_label_str = f"Player {player} Cards"
    bg_color = player_label_color
  exec(f"h_p{player}_label = ttk.Label(h_board_frame, text=player_label_str,"
  f"relief=label_relief_default, width=player_label_width,"
  f"padding=label_padding_default, background=bg_color, anchor='center')")
  # Card display labels
  exec(f"h_p{player}_c1_lbl = ttk.Label(h_board_frame, image=c52_img, padding=card_padding_default)")
  exec(f"h_p{player}_c2_lbl = ttk.Label(h_board_frame, image=c52_img, padding=card_padding_default)")

# Community card widgets
h_com_label = ttk.Label(h_board_frame, text="Community Cards", relief=label_relief_default,
width=community_label_width, padding=label_padding_default, background=player_label_color,
anchor='center')
for card in range(1,6):
  # Card display labels
  exec(f"h_com_c{card}_lbl = ttk.Label(h_board_frame, image=c52_img, padding=card_padding_default)")

# Rest of widgets
h_win_label = ttk.Label(h_root_frame, text="Win %", relief=label_relief_default,
width=results_label_width, padding=label_padding_default, background=results_label_color, anchor='center')
h_win_result = ttk.Label(h_root_frame, textvariable=win_pct, relief=result_relief, width=results_label_width,
padding=label_padding_default, anchor='center')
h_tie_label = ttk.Label(h_root_frame, text="Tie %", relief=label_relief_default,
width=results_label_width, padding=label_padding_default, background=results_label_color, anchor='center')
h_tie_result = ttk.Label(h_root_frame, textvariable=tie_pct, relief=result_relief, width=results_label_width,
padding=label_padding_default, anchor='center')
h_lose_label = ttk.Label(h_root_frame, text="Lose %", relief=label_relief_default,
width=results_label_width, padding=label_padding_default, background=results_label_color, anchor='center')
h_lose_result = ttk.Label(h_root_frame, textvariable=lose_pct, relief=result_relief, width=results_label_width,
padding=label_padding_default, anchor='center')
h_trials_label = ttk.Label(h_root_frame, text="# of Trials", relief=label_relief_default,
width=trials_label_width, padding=label_padding_default, background=option_label_color, anchor='center')
h_trials_entry = ttk.Entry(h_root_frame, textvariable=num_trials, justify='right', width=trials_label_width+1)
h_num_opp_label = ttk.Label(h_root_frame, text="# of Opponents", relief=label_relief_default,
width=num_opp_label_width, padding=label_padding_default, background=option_label_color, anchor='center')
h_num_opp_lb = ttk.Combobox(h_root_frame, textvariable=num_opp, values=(1,2,3,4,5,6,7,8), width=num_opp_label_width-10)
h_run_btn = ttk.Button(h_root_frame, text="Run", width=btn_width_default, command=run_simulation)
h_report_btn = ttk.Button(h_root_frame, text="Report", width=btn_width_default, command=run_report)
h_load_btn = ttk.Button(h_root_frame, text="Load", width=btn_width_default, command=run_load)
h_save_btn = ttk.Button(h_root_frame, text="Save", width=btn_width_default, command=run_save)
h_clear_cards_btn = ttk.Button(h_root_frame, text="Clear Cards", width=btn_width_default, command=clear_all_cards)
h_toggle_pct_plot = ttk.Checkbutton(h_root_frame, text="Plot % History", variable=plot_pct_history)
#------------------------------------------------------------------------------

# Place widgets ---------------------------------------------------------------
h_root_frame.place(relx=0.5, rely=0.5, anchor='center')
# Player widgets
for player in range(initial_num_opp + 1):
  exec(f"h_p{player}_label.place(x=p{player}_start[0], y=p{player}_start[1])")
  exec(f"h_p{player}_c1_lbl.place(x=p{player}_start[0], y=p{player}_start[1] + card_y_lbl_offset)")
  exec(f"h_p{player}_c2_lbl.place(x=p{player}_start[0] + card_x_offset, y=p{player}_start[1] + card_y_lbl_offset)")
h_com_label.place(x=com_start[0], y=com_start[1])
for card in range(1,6):
  x = com_start[0] + (card - 1) * card_x_offset
  exec(f"h_com_c{card}_lbl.place(x=x, y=com_start[1] + card_y_lbl_offset)")
h_win_label.place(x=results_start[0], y=results_start[1])
h_win_result.place(x=results_start[0] + results_x_space, y=results_start[1])
h_tie_label.place(x=results_start[0], y=results_start[1] + result_y_space)
h_tie_result.place(x=results_start[0] + results_x_space, y=results_start[1] + result_y_space)
h_lose_label.place(x=results_start[0], y=results_start[1] + 2 * result_y_space)
h_lose_result.place(x=results_start[0] + results_x_space, y=results_start[1] + 2 * result_y_space)
h_trials_label.place(x=trials_start[0], y=trials_start[1])
h_trials_entry.place(x=trials_start[0]+1, y=trials_start[1] + result_y_space)
h_num_opp_label.place(x=num_opp_start[0], y=num_opp_start[1])
h_num_opp_lb.place(x=num_opp_start[0] + num_opp_x_space, y=num_opp_start[1] + result_y_space)
h_clear_cards_btn.place(x=clear_cards_start[0], y=clear_cards_start[1])
h_toggle_pct_plot.place(x=clear_cards_start[0], y=clear_cards_start[1] - 30)
h_board_frame.place(x=0,y=0)
h_run_btn.place(x=btn_start[0], y=btn_start[1])
h_report_btn.place(x=btn_start[0] + btn_x_space, y=btn_start[1])
h_load_btn.place(x=btn_start[0] + 2 * btn_x_space, y=btn_start[1])
h_save_btn.place(x=btn_start[0] + 3 * btn_x_space, y=btn_start[1])
#------------------------------------------------------------------------------

# Key bindings
for player in range(0,9):
  exec(f"h_p{player}_c1_lbl.bind('<Button-1>', partial(choose_card, player={player}, card_pos=1))")
  exec(f"h_p{player}_c2_lbl.bind('<Button-1>', partial(choose_card, player={player}, card_pos=2))")
for card in range(1,6):
  exec(f"h_com_c{card}_lbl.bind('<Button-1>', partial(choose_card, player=com_player_num, card_pos={card}))")
h_num_opp_lb.bind('<<ComboboxSelected>>', update_num_opp)

# Run GUI
h_root.mainloop()
