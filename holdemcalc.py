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
import requests


# Functions -------------------------------------------------------------------

def submit_card(*args, h_win, player, card_pos):
  """Callback for submit button in the card select popup window
  *args = arguments passed by tkinter
  h_win = handle to card selection window
  player = index of player selecting the card
  card_pos = index representing which card of the player or community cards
  Function will update the global card list to reflect the card selected, the
  player index and card index will determine which card in the list to update
  """
  global g_cards
  # Update the cards list with the last toggled card state
  current_card_index = 2 * player + card_pos
  g_cards[current_card_index] = g_card_toggle
  # Change player's or community card image in main GUI to the new card
  g_card_labels[current_card_index].configure(image=g_card_images[g_card_toggle])
  h_win.destroy()


def toggle_card(*args, card, card_handles):
  """Callback for submit button in the card select popup window
  *args = arguments passed by tkinter
  card = is the value of card that was clicked
  card_handles = a list of label handles of the 52 cards in the selection popup window
  Function will respond to the user left clicking event on one of the card label
  images in the popup window. If user selects or deselects a card the global
  variable g_card_toggle will be updated accordingly, once the user presses
  submit this g_card_toggle variable will be use to assign to the global card
  list
  """
  global g_card_toggle
  # Check if user re-selected the same card or if it is a new selection
  if card == g_card_toggle:
    # They re-selected their card, which means unselect and set to random
    card_handles[card].configure(background='#ffffff')
    g_card_toggle = 52
  else:
    # They picked a new card, if their previous card wasn't random, unselect it
    if g_card_toggle != 52:
      card_handles[g_card_toggle].configure(background='#ffffff')
    # Select the new card by highlighting it and setting g_card_toggle
    card_handles[card].configure(background='#33ff33')
    g_card_toggle = card


def choose_card(*args, player, card_pos):
  """Callback for left click event on a card in main GUI window
  *args = arguments passed by tkinter
  player = index of player selecting the card
  card_pos = index representing which card of the player or community cards
  Function will launch a popup card selection window to allow user to select
  or unselect their cards, uses global variables g_card_toggle and g_cards
  """
  global g_cards, g_card_toggle
  # Initialize g_card_toggle to the currently selected card from the global list
  current_card_index = 2 * player + card_pos
  g_card_toggle = g_cards[current_card_index]
  # Get list of all cards that are chosen, except for the current card, to make them blank in the popup
  chosen_cards = g_cards[:]
  del chosen_cards[current_card_index]
  # Create popup winddow
  card_xspace = 70
  card_yspace = 95
  win_width = card_xspace * 13
  win_height = card_yspace * 4 + 60
  popup = Toplevel(h_root)
  popup.geometry(f"{win_width}x{win_height}")
  popup.geometry(f"+{h_root.winfo_rootx()+main_window_width//2-win_width//2}"
                 f"+{h_root.winfo_rooty()+main_window_height//2-win_height//2}")
  # Create card labels and bind click callback to them if available to select
  card_handles = []
  for card in range(52):
    card_handles.append(ttk.Label(popup,image=g_card_images[card], padding='5 5 5 5', relief='groove'))
    card_handles[card].place(x=(card%13)*card_xspace, y=(card//13)*card_yspace)
    # If card selected in main GUI is one of the 52, then highlight it in picker window
    if card == g_card_toggle:
      card_handles[card].configure(background='#33ff33')
    # If card is in chosen_card list then remove its image and unbind the callback, else bind callback
    if card in chosen_cards:
      card_handles[card].unbind('<Button-1>')
      card_handles[card].configure(image=g_card_images[53])
    else:
      card_handles[card].bind('<Button-1>', partial(toggle_card, card=card, card_handles=card_handles))
  # Create submit and cancel buttons for popup
  ttk.Button(popup, text="Submit", padding="6 6 6 6", \
    command=partial(submit_card, h_win=popup, player=player, card_pos=card_pos)).place(x=win_width//2-100,y=win_height-50)
  ttk.Button(popup, text="Cancel", padding="6 6 6 6", \
    command=lambda h_win=popup: h_win.destroy()).place(x=win_width//2-0,y=win_height-50)
  # Block main window callbacks until popup is closed
  popup.grab_set()


def update_num_opp(*args):
  """Callback for drop-down list to set the # of opponents
  *args = arguments passed by tkinter
  Function erase or add the necessary amount of opponents based
  on the number selected in the drop-down, uses g_cards to keep track of all cards
  """
  global g_cards
  no = int(num_opp.get())
  # Show all players up to num_opp
  for player in range(no + 1):
    x, y = eval(f"p{player}_start")
    g_player_labels[player].place(x=x, y=y)
    y += card_y_lbl_offset
    g_card_labels[2 * player].place(x=x, y=y)
    x += card_x_offset
    g_card_labels[2 * player + 1].place(x=x, y=y)
  # Hide all players above num_opp and and set their cards to random
  for player in range(no + 1, 9):
    # Hide player label
    g_player_labels[player].place_forget()
    # Hide player cards and set card to random
    for card_pos in range(2):
      g_cards[2 * player + card_pos] = 52
      g_card_labels[2 * player + card_pos].place_forget()
      g_card_labels[2 * player + card_pos].configure(image=g_card_images[52])


def check_num_trials(*args):
  """Callback for text entry box for the # of trials to run
  *args = arguments passed by tkinter
  Function will check the entry typed in the box, if not a valid
  integer >0 and <=num_trials_max then an error message is displayed
  and # of trials is set to 5000
  """
  entry = num_trials.get()
  if len(entry) !=0 and not num_trials.get().isnumeric():
    messagebox.showerror(title="Bad Input", message="# of Trials must be a positive integer.")
    num_trials.set(value=5000)
  elif len(entry) !=0 and int(entry) > num_trials_max:
    num_trials.set(value=num_trials_max)


def clear_all_cards(*args):
  """Callback for clear cards button
  *args = arguments passed by tkinter
  Function will iterate through player and community cards and set all
  cards back to random, making all cards available to choose from
  """
  global g_cards
  num_players = int(num_opp.get()) + 1
  # Clear fixed cards for players, set to random card and random card image
  for player in range(num_players):
    for card_pos in range(2):
      g_cards[2 * player + card_pos] = 52
      g_card_labels[2 * player + card_pos].configure(image=g_card_images[52])
  # Clear fixed cards for community cards, set to random card and random card image
  for card_pos in range(5):
    g_cards[2 * 9 + card_pos] = 52
    g_card_labels[2 * 9 + card_pos].configure(image=g_card_images[52])


def is_valid_fname(fname):
  """Function to validate a filename entry
  fname = string representing entered filename
  Function will check filenames to be alphanumeric with underscore,
  space, or dash and return a boolean
  """
  if re.search(r'[^A-Za-z0-9_ \-]', fname):
    messagebox.showerror(title="Error", message="Illegal Filename!")
    return False
  else:
    return True


def run_save(*args):
  """Callback for save button
  *args = arguments passed by tkinter
  Function will collect all the simulation configuration info, prompt
  user for a filename, and if valid will store it in the ./Save directory
  """
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
  """Callback for load button
  *args = arguments passed by tkinter
  Function will read in the simulation configuration settings from a .sim file
  and apply all the settings to the main GUI
  """
  global g_cards
  sim_config = dict()
  # Choose file to load
  fname = filedialog.askopenfilename(initialdir=os.getcwd() + '/Save', filetypes=[("Sim Files", "*.sim")])
  if len(fname) == 0:
    return
  fh = open(fname, 'r')
  # Extract first line
  num_runs, num_opponents, calc_percentages = fh.readline().strip().split()
  # Extract player cards and set images
  for player in range(int(num_opponents) + 1):
    cards =  fh.readline().strip().split()
    card1 = int(cards[0])
    card2 = int(cards[1])
    g_cards[2 * player] = card1
    g_cards[2 * player + 1] = card2
    g_card_labels[2 * player].configure(image=g_card_images[card1])
    g_card_labels[2 * player + 1].configure(image=g_card_images[card2])
  # Extract community cards and set images
  cards =  fh.readline().strip().split()
  for card_pos in range(5):
    card = int(cards[card_pos])
    g_cards[2 * 9 + card_pos] = card
    g_card_labels[2 * 9 + card_pos].configure(image=g_card_images[card])
  fh.close()
  # Set option GUI variables
  num_trials.set(num_runs)
  num_opp.set(num_opponents)
  win_pct.set("------")
  tie_pct.set("------")
  loss_pct.set("------")
  plot_pct_history.set(calc_percentages)
  # Clear unused players and their cards
  update_num_opp()


def run_report(*args):
  """Callback for report button
  *args = arguments passed by tkinter
  Function will make an API call to teammates microservice and pass
  a list of all the simulations performed while the application was open
  the microservice will return an html file which is a formatted table of results
  """
  headers = {"Content-Type": "application/json"}
  res = requests.post(API, json=g_simulation_history, headers=headers)
  fh = open(REPORT_FNAME, 'w')
  fh.write(res.text)
  fh.close()
  os.system(f"start {REPORT_FNAME}")


def get_simulation_setup(sim_config):
  """Function to collect current simulation configuration
  sim_config = dictionary to hold the simulation setting info
  """
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
  """Callback for run button
  *args = arguments passed by tkinter
  Function will write all the simulation configuration info to
  a input file which is used by the simulation engine to perform
  a monte carlo simulation to estimate win/loss/tie percentages
  After results are returned the GUI and graphs are updated with
  the simulation results
  """
  global g_cards, g_simulation_history, g_sim_num
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
  loss_pct.set(f"{float(results[2]) * 100:.2f}")
  # Plot percentage history if necessary
  if plot_pct_history.get() == '1':
    plot_percentages(sim_config)
  # Save simulation in history list for report
  g_sim_num += 1
  sim_history = dict()
  sim_history['sim_number'] = g_sim_num
  sim_history['num_trials'] = num_trials.get()
  sim_history['num_opponents'] = num_opp.get()
  sim_history['user_cards'] = g_cards[0:2]
  sim_history['opponent_cards'] = []
  for op in range(1,int(num_opp.get()) + 1):
    sim_history['opponent_cards'].append(g_cards[2 * op:2 * (op + 1)])
  sim_history['community_cards'] = g_cards[2 * 9:2 * 9 + 5]
  sim_history['win_pct'] = win_pct.get()
  sim_history['tie_pct'] = tie_pct.get()
  sim_history['loss_pct'] = loss_pct.get()
  g_simulation_history.append(sim_history)
  #DEBUG
  if DEBUG:
    print(f"\nSim Config:")
    print(f"\t# of runs = {sim_config['num_runs']}")
    print(f"\t# of opponents = {sim_config['num_opponents']}")
    print(f"\tDo Percentages = {sim_config['calc_percentages']}")
    for player in range(sim_config['num_opponents'] + 1):
      print(f"\tPlayer #{player} cards = ({g_cards[2 * player]}, {g_cards[2 * player + 1]})")
    cards = g_cards[2 * 9:2 * 9 + 5]
    print(f"\tCommunity cards = ({cards[0]}, {cards[1]}, {cards[2]}, {cards[3]}, {cards[4]})")
  #DEBUG


def plot_percentages(sim_config):
  num_runs = sim_config['num_runs']
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


def run_help(*args):
  """Callback for help button in main GUI
  *args = arguments passed by tkinter
  Function will launch a popup window with instructions on how to use the software
  """
  # Create popup winddow
  win_width = 700
  win_height = 435
  popup = Toplevel(h_root)
  popup.geometry(f"{win_width}x{win_height}")
  popup.geometry(f"+{h_root.winfo_rootx()+main_window_width}"
                 f"+{h_root.winfo_rooty()+main_window_height//2-win_height//2}")
  popup.resizable(False, False)
  popup.title('Help')
    # Create test area for help instructions
  with open(HELP_FNAME, 'r') as f:
    lines = f.readlines()
  help_str = ''.join(lines)
  h_text_frame = ttk.Frame(popup, width=win_width, height=win_height, relief="groove", padding="5 5 5 5")
  h_text_frame.place(relx=0.5, rely=0.5, anchor='center')
  h_help_text_lbl = ttk.Label(h_text_frame, text=help_str, justify=LEFT,
  padding="10 10 10 10", background="#ffffff", anchor='center')
  h_help_text_lbl.place(x=20, y=20)
#------------------------------------------------------------------------------


# Global variables ------------------------------------------------------------
DEBUG = 0
API = "https://showboat-rest-api.herokuapp.com/report-generator"
REPORT_FNAME = "Report.html"
HELP_FNAME = "help.txt"
CARD_INT_TO_STR = {
                    0:  '2C',  1: '3C',  2: '4C',   3: '5C',  4: '6C',  5: '7C',
                    6:  '8C',  7: '9C',  8: '10C',  9: 'JC', 10: 'QC', 11: 'KC', 12: 'AC',
                    13: '2D', 14: '3D', 15: '4D',  16: '5D', 17: '6D', 18: '7D',
                    19: '8D', 20: '9D', 21: '10D', 22: 'JD', 23: 'QD', 24: 'KD', 25: 'AD',
                    26: '2H', 27: '3H', 28: '4H',  29: '5H', 30: '6H', 31: '7H',
                    32: '8H', 33: '9H', 34: '10H', 35: 'JH', 36: 'QH', 37: 'KH', 38: 'AH',
                    39: '2S', 40: '3S', 41: '4S',  42: '5S', 43: '6S', 44: '7S',
                    45: '8S', 46: '9S', 47: '10S', 48: 'JS', 49: 'QS', 50: 'KS', 51: 'AS', 52: '?'
                  }
CARD_INT_TO_STR2 = {
                    0:  '2 of C',  1: '3 of C',  2:  '4 of C',  3: '5 of C',  4: '6 of C',  5: '7 of C',
                    6:  '8 of C',  7: '9 of C',  8: '10 of C',  9: 'J of C', 10: 'Q of C', 11: 'K of C', 12: 'A of C',
                    13: '2 of D', 14: '3 of D', 15:  '4 of D', 16: '5 of D', 17: '6 of D', 18: '7 of D',
                    19: '8 of D', 20: '9 of D', 21: '10 of D', 22: 'J of D', 23: 'Q of D', 24: 'K of D', 25: 'A of D',
                    26: '2 of H', 27: '3 of H', 28:  '4 of H', 29: '5 of H', 30: '6 of H', 31: '7 of H',
                    32: '8 of H', 33: '9 of H', 34: '10 of H', 35: 'J of H', 36: 'Q of H', 37: 'K of H', 38: 'A of H',
                    39: '2 of S', 40: '3 of S', 41:  '4 of S', 42: '5 of S', 43: '6 of S', 44: '7 of S',
                    45: '8 of S', 46: '9 of S', 47: '10 of S', 48: 'J of S', 49: 'Q of S', 50: 'K of S', 51: 'A of S', 52: '?'
                   }
calculator_input_fname   = "input.txt"
calculator_results_fname = "calcResults.txt"
calculator_percent_fname = "calcPercents.dat"
calculator_service_fname = "calcService.txt"
sim_service_fname        = "holdem_service.txt"
com_player_num  = 9
initial_num_opp = 1
num_trials_init = 5000
num_trials_max  = 10000000
g_player_labels = []
g_card_labels = []
g_card_images = []
# Non-constant globals
g_cards = [52] * 23
g_card_toggle = 52
g_sim_num = 0
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
style = ttk.Style()
style.theme_use('alt')

# Load card images into global list
for card in range(53):
  fname = os.getcwd() + "\\CARDS\\" + f"{card}.png"
  card_img = Image.open(fname)
  card_img = card_img.resize((card_width, card_height), Image.Resampling.LANCZOS)
  card_img = ImageTk.PhotoImage(card_img)
  g_card_images.append(card_img)
card_img = Image.open(".\\CARDS\\None.jpg")
card_img = card_img.resize((card_width, card_height), Image.Resampling.LANCZOS)
card_img = ImageTk.PhotoImage(card_img)
g_card_images.append(card_img)

# GUI variables
num_trials = StringVar(value=f"{num_trials_init}")
num_trials.trace_add("write", check_num_trials)
num_opp = StringVar(value=initial_num_opp)
win_pct = StringVar(value="------")
tie_pct = StringVar(value="------")
loss_pct = StringVar(value="------")
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
  player_label = ttk.Label(h_board_frame, text=player_label_str, relief=label_relief_default,
  width=player_label_width, padding=label_padding_default, background=bg_color, anchor='center')
  g_player_labels.append(player_label)
  # Card display labels
  g_card_labels.append(ttk.Label(h_board_frame, image=g_card_images[52], padding=card_padding_default))
  g_card_labels.append(ttk.Label(h_board_frame, image=g_card_images[52], padding=card_padding_default))

# Community card widgets
h_com_label = ttk.Label(h_board_frame, text="Community Cards", relief=label_relief_default,
width=community_label_width, padding=label_padding_default, background=player_label_color,
anchor='center')
# Card display labels
for card in range(5):
  g_card_labels.append(ttk.Label(h_board_frame, image=g_card_images[52], padding=card_padding_default))

# Rest of widgets
h_win_label = ttk.Label(h_root_frame, text="Win %", relief=label_relief_default,
width=results_label_width, padding=label_padding_default, background=results_label_color, anchor='center')
h_win_result = ttk.Label(h_root_frame, textvariable=win_pct, relief=result_relief, width=results_label_width,
padding=label_padding_default, anchor='center', background="#eeeeee")
h_loss_label = ttk.Label(h_root_frame, text="Loss %", relief=label_relief_default,
width=results_label_width, padding=label_padding_default, background=results_label_color, anchor='center')
h_loss_result = ttk.Label(h_root_frame, textvariable=loss_pct, relief=result_relief, width=results_label_width,
padding=label_padding_default, anchor='center', background="#eeeeee")
h_tie_label = ttk.Label(h_root_frame, text="Tie %", relief=label_relief_default,
width=results_label_width, padding=label_padding_default, background=results_label_color, anchor='center')
h_tie_result = ttk.Label(h_root_frame, textvariable=tie_pct, relief=result_relief, width=results_label_width,
padding=label_padding_default, anchor='center', background="#eeeeee")
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
h_help_btn = ttk.Button(h_root_frame, text="Help", width=btn_width_default, command=run_help)
#------------------------------------------------------------------------------

# Place widgets ---------------------------------------------------------------
h_root_frame.place(relx=0.5, rely=0.5, anchor='center')
# Player widgets
for player in range(initial_num_opp + 1):
  x, y = eval(f"p{player}_start")
  g_player_labels[player].place(x=x, y=y)
  g_card_labels[2 * player].place(x=x, y=y + card_y_lbl_offset)
  g_card_labels[2 * player + 1].place(x=x + card_x_offset, y=y + card_y_lbl_offset)
# Community card widgets
h_com_label.place(x=com_start[0], y=com_start[1])
for card in range(5):
  x = com_start[0] + card * card_x_offset
  g_card_labels[2 * 9 + card].place(x=x, y=com_start[1] + card_y_lbl_offset)
# Remaining widgets
h_win_label.place(x=results_start[0], y=results_start[1])
h_win_result.place(x=results_start[0] + results_x_space, y=results_start[1])
h_loss_label.place(x=results_start[0], y=results_start[1] + result_y_space)
h_loss_result.place(x=results_start[0] + results_x_space, y=results_start[1] + result_y_space)
h_tie_label.place(x=results_start[0], y=results_start[1] + 2 * result_y_space)
h_tie_result.place(x=results_start[0] + results_x_space, y=results_start[1] + 2 * result_y_space)
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
h_help_btn.place(x=btn_start[0] + 3 * btn_x_space, y=btn_start[1] - 50)
#------------------------------------------------------------------------------

# Key bindings
for player in range(9):
  for card_pos in range(2):
    g_card_labels[2 * player + card_pos].bind('<Button-1>', partial(choose_card, player=player, card_pos=card_pos))
for card_pos in range(5):
  g_card_labels[2 * 9 + card_pos].bind('<Button-1>', partial(choose_card, player=com_player_num, card_pos=card_pos))
h_num_opp_lb.bind('<<ComboboxSelected>>', update_num_opp)

# Run GUI
h_root.mainloop()
