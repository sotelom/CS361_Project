from Card import Card
from functools import partial
from tkinter import *
from tkinter import ttk

# Functions -------------------------------------------------------------------
def create_deck(L):
  for i in range(4):
    for j in range(13):
      L.append(Card(j, i))
  return L

def mark_used(deck, value_str, state):
  card_values = {'2':0,'3':1,'4':2,'5':3,'6':4,'7':5,'8':6,'9':7,'10':8,'J':9,
  'Q':10,'K':11,'A':12}
  suit_values = {'C':0,'D':1,'H':2,'S':3}
  tokens = value_str.strip().split()
  index = card_values[tokens[0]] + 13 * suit_values[tokens[2]]
  deck[index].set_used(state)

def get_deck_values(deck):
  L = []
  for c in deck:
    if not c.is_used():
      L.append(c.get_str_value())
  return L

def update_card_list(*args, deck, player, card_pos):
  if player == com_player_num:
    prefix = "com"
  else:
    prefix = f"p{player}"
  # Get Players previously selected card
  prev_card_str = eval(f"{prefix}_c{card_pos}_lbl.get()")
  # Get Players newly selected card
  new_card_str = eval(f"{prefix}_c{card_pos}.get()")
  # Make available in deck if necessary
  if not (prev_card_str == '?' or prev_card_str == new_card_str):
    # There was a previous card and the new selection is different, so free previous
    mark_used(deck, prev_card_str, False)
  # Set players card in display label
  eval(f"{prefix}_c{card_pos}_lbl.set(new_card_str)")
  # Mark new card choice as used
  mark_used(deck, new_card_str, True)
  # Update all card lists
  update_all_card_lists(deck)
  #DEBUG
  if player == com_player_num:
    print(f"Community selected {new_card_str} for card#{card_pos}")
  else:
    print(f"player {player} selected {new_card_str} for card#{card_pos}")
  #DEBUG


def toggle_fixed_cards(*args, player, card_pos):
  if player == com_player_num:
    # Community cards toggled
    state = eval(f"com_c{card_pos}_fix.get()")
    prefix = "com"
  else:
    state = eval(f"p{player}_c{card_pos}_fix.get()")
    prefix = f"p{player}"
  if state == "1":
    # Set intial card selection to empty
    eval(f"{prefix}_c{card_pos}.set('')")
    # Make Drop-down list appear
    x = eval(f"{prefix}_start[0]") + (card_pos - 1) * card_x_offset
    y = eval(f"{prefix}_start[1] + card_y_cb_offset")
    eval(f"h_{prefix}_c{card_pos}_lb.place(x=x,y=y)")
  else:
    card_str = eval(f"{prefix}_c{card_pos}_lbl.get()")
    # Make fixed card available in deck if necessary
    if card_str != '?':
      mark_used(deck, card_str, False)
    # Set card label to random
    eval(f"{prefix}_c{card_pos}_lbl.set('?')")
    # Update all card lists
    update_all_card_lists(deck)
    # Make Drop-down list disappear
    eval(f"h_{prefix}_c{card_pos}_lb.place_forget()")

def update_num_opp(*args, deck):
  no = int(num_opp.get())
  for player in range(no + 1):
    exec(f"h_p{player}_label.place(x=p{player}_start[0], y=p{player}_start[1])")
    exec(f"h_p{player}_c1_lbl.place(x=p{player}_start[0], y=p{player}_start[1] + card_y_lbl_offset)")
    exec(f"h_p{player}_c2_lbl.place(x=p{player}_start[0] + card_x_offset, y=p{player}_start[1] + card_y_lbl_offset)")
    exec(f"h_p{player}_c1_cb.place(x=p{player}_start[0], y=p{player}_start[1] + card_y_card_offset)")
    exec(f"h_p{player}_c2_cb.place(x=p{player}_start[0] + card_x_offset, y=p{player}_start[1] + card_y_card_offset)")
  for player in range(no + 1, 9):
    # Hide player label
    exec(f"h_p{player}_label.place_forget()")
    for card_pos in range(1, 3):
      # Reset fixed states and card labels and return cards to available if necessary
      state = eval(f"p{player}_c{card_pos}_fix.get()")
      if state == '1':
        # Set fixed state to unchecked
        eval(f"p{player}_c{card_pos}_fix.set('0')")
        # Get the last card that was used
        card_str = eval(f"p{player}_c{card_pos}.get()")
        # if not random make available
        if card_str != '?':
          #DEBUG
          print(f"removing card {card_str}, from player#{player}, card#{card_pos}")
          #DEBUG
          mark_used(deck, card_str, False)
        # Set card label to random
        eval(f"p{player}_c{card_pos}_lbl.set('?')")
      # Hide rest of player widgets
      exec(f"h_p{player}_c{card_pos}_lbl.place_forget()")
      exec(f"h_p{player}_c{card_pos}_cb.place_forget()")
      exec(f"h_p{player}_c{card_pos}_lb.place_forget()")
    # Update all card lists
    update_all_card_lists(deck)

def update_all_card_lists(deck):
  values = get_deck_values(deck)
  # Update all card lists with values
  for player in range(9):
    for card_pos in range(1, 3):
      exec(f"h_p{player}_c{card_pos}_lb['values'] = values")
  for card_pos in range(1, 5):
    exec(f"h_com_c{card_pos}_lb['values'] = values")

def run_save(*args):
  pass

def run_load(*args):
  pass

def run_report(*args):
  pass

def run_simulation(*args):
  pass
#------------------------------------------------------------------------------



# GUI Settings ----------------------------------------------------------------
main_title = "Hold'em Odds"
main_window_width = 930
main_window_height = 525
board_window_width = 920
root_frame_padding = "5 5 5 5"
label_relief_default = 'ridge'
label_padding_default = "5 5 5 5"
player_label_width = 21
player_label_color = "#99ffff"
user_label_color = "#66ff66"
option_label_color = "#ffff66"
results_label_color = "#66ff66"
trials_label_width = 12
results_label_width = 10
community_label_width = 62
card_frame_width = 100
card_frame_height = 50
card_padding_default = "3 3 3 3"
card_label_width = 8
num_opp_label_width = 15
btn_width_default = 10
cards_relief = "sunken"
result_relief = "sunken"
card_y_lbl_offset = 33
card_x_offset = 82
card_y_card_offset = card_y_lbl_offset + 24
card_y_cb_offset = card_y_card_offset + 22
p6_start = (80, 80)
p7_start = (p6_start[0] - 60, p6_start[1] + 120)
p5_start = (p6_start[0] + 152 + 45, p6_start[1] - 50)
p4_start = (p5_start[0] + 152 + 55, p5_start[1])
p3_start = (p4_start[0] + 152 + 45, p6_start[1])
p2_start = (p3_start[0] + 60, p3_start[1] + 120)
p1_start = (p2_start[0] - 25 - 152, p2_start[1] + 80)
p0_start = (p1_start[0] - 30 - 152, p1_start[1])
p8_start = (p0_start[0] - 30 - 152, p0_start[1])
com_start = (p6_start[0] + 152 + 25, p3_start[1] + 70)
results_start = (p0_start[0], p0_start[1] + 125)
result_y_space = 35
results_x_space = 80
trials_start = (10, results_start[1] + 45)
num_opp_start = (trials_start[0] + 95, trials_start[1])
num_opp_x_space = 50
frame_space = 5
cards_frame_start = (board_window_width + frame_space, 0)
btn_x_space = 75
btn_start = (results_start[0] + results_x_space + 150, results_start[1] + 2 * result_y_space)
# -----------------------------------------------------------------------------


# Main window
h_root = Tk()
h_root.title(main_title)
h_root.geometry(f"{main_window_width}x{main_window_height}")
h_root.resizable(False, False)
h_root_frame = ttk.Frame(h_root, padding = root_frame_padding, width=main_window_width, height=main_window_height)
#h_cards_frame = ttk.Frame(h_root_frame, width=main_window_width-board_window_width-frame_space-10,
#height=main_window_height-130, relief="groove")
h_board_frame = ttk.Frame(h_root_frame, width=board_window_width, height=main_window_height-130, relief="groove")


# Global GUI variables ------------------------
deck = create_deck([])
com_player_num = -1
initial_num_opp = 1
# Player card variables
for player in range(9):
  exec(f"p{player}_c1 = StringVar()")
  exec(f"p{player}_c1_lbl = StringVar(value='?')")
  exec(f"p{player}_c1_fix = StringVar(value=0)")
  exec(f"p{player}_c2 = StringVar()")
  exec(f"p{player}_c2_lbl = StringVar(value='?')")
  exec(f"p{player}_c2_fix = StringVar(value=0)")
# Community card variables
for card in range(1,6):
  exec(f"com_c{card} = StringVar()")
  exec(f"com_c{card}_lbl = StringVar(value='?')")
  exec(f"com_c{card}_fix = StringVar(value=0)")
num_trials = StringVar(value=10000)
num_opp = StringVar(value=initial_num_opp)
win_pct = StringVar()
tie_pct = StringVar()
lose_pct = StringVar()
# ---------------------------------------------


# Main frame in window --------------------------------------------------------
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
  exec(f"h_p{player}_c1_lbl = ttk.Label(h_board_frame, textvariable=p{player}_c1_lbl,"
  f"relief=cards_relief, width=card_label_width, background='#fff',"
  f"padding=card_padding_default)")
  exec(f"h_p{player}_c2_lbl = ttk.Label(h_board_frame, textvariable=p{player}_c2_lbl,"
  f"relief=cards_relief, width=card_label_width, background='#fff',"
  f"padding=card_padding_default)")
  # Checkboxes to toggle manual selection
  exec(f"h_p{player}_c1_cb = ttk.Checkbutton(h_board_frame, text='Fix',"
  f"variable=p{player}_c1_fix, command=partial(toggle_fixed_cards, player={player}, card_pos=1)," f"width=card_label_width)")
  exec(f"h_p{player}_c2_cb = ttk.Checkbutton(h_board_frame, text='Fix',"
  f"variable=p{player}_c2_fix, command=partial(toggle_fixed_cards, player={player}, card_pos=2)," f"width=card_label_width)")
  # Dropdown lists to select fixed cards
  exec(f"h_p{player}_c1_lb = ttk.Combobox(h_board_frame,"
  f"textvariable=p{player}_c1, values=get_deck_values(deck), width=card_label_width)")
  exec(f"h_p{player}_c2_lb = ttk.Combobox(h_board_frame,"
  f"textvariable=p{player}_c2, values=get_deck_values(deck), width=card_label_width)")
# Community card widgets
h_com_label = ttk.Label(h_board_frame, text="Community Cards", relief=label_relief_default,
width=community_label_width, padding=label_padding_default, background=player_label_color,
anchor='center')
for card in range(1,6):
  # Card display labels
  exec(f"h_com_c{card}_lbl = ttk.Label(h_board_frame, textvariable=com_c{card}_lbl,"
  f"relief=cards_relief, width=card_label_width, background='#fff',"
  f"padding=card_padding_default)")
  # Checkboxes to toggle manual selection
  exec(f"h_com_c{card}_cb = ttk.Checkbutton(h_board_frame, text='Fix',"
  f"variable=com_c{card}_fix, command=partial(toggle_fixed_cards, player=com_player_num, card_pos={card}),"
  f"width=card_label_width)")
  # Dropdown list to select fixed cards
  exec(f"h_com_c{card}_lb = ttk.Combobox(h_board_frame,"
  f"textvariable=com_c{card}, values=get_deck_values(deck), width=card_label_width)")
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

#------------------------------------------------------------------------------

# Place widgets ---------------------------------------------------------------
h_root_frame.place(relx=0.5, rely=0.5, anchor='center')
# Player widgets
for player in range(initial_num_opp + 1):
  exec(f"h_p{player}_label.place(x=p{player}_start[0], y=p{player}_start[1])")
  exec(f"h_p{player}_c1_lbl.place(x=p{player}_start[0], y=p{player}_start[1] + card_y_lbl_offset)")
  exec(f"h_p{player}_c2_lbl.place(x=p{player}_start[0] + card_x_offset, y=p{player}_start[1] + card_y_lbl_offset)")
  exec(f"h_p{player}_c1_cb.place(x=p{player}_start[0], y=p{player}_start[1] + card_y_card_offset)")
  exec(f"h_p{player}_c2_cb.place(x=p{player}_start[0] + card_x_offset, y=p{player}_start[1] + card_y_card_offset)")
  # Temporary
  #exec(f"h_p{player}_c1_lb.place(x=p{player}_start[0], y=p{player}_start[1] + card_y_cb_offset)")
  #exec(f"h_p{player}_c2_lb.place(x=p{player}_start[0] + card_x_offset, y=p{player}_start[1] + card_y_cb_offset)")
h_com_label.place(x=com_start[0], y=com_start[1])
for card in range(1,6):
  x = com_start[0] + (card - 1) * card_x_offset
  exec(f"h_com_c{card}_lbl.place(x=x, y=com_start[1] + card_y_lbl_offset)")
  exec(f"h_com_c{card}_cb.place(x=x, y=com_start[1] + card_y_card_offset)")
  # Temporary
  #exec(f"h_com_c{card}_lb.place(x=x, y=com_start[1] + card_y_cb_offset)")
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
h_board_frame.place(x=0,y=0)
h_run_btn.place(x=btn_start[0], y=btn_start[1])
h_report_btn.place(x=btn_start[0] + btn_x_space, y=btn_start[1])
h_load_btn.place(x=btn_start[0] + 2 * btn_x_space, y=btn_start[1])
h_save_btn.place(x=btn_start[0] + 3 * btn_x_space, y=btn_start[1])
#h_cards_frame.place(x=cards_frame_start[0],y=cards_frame_start[1])
#------------------------------------------------------------------------------

# Key bindings
for player in range(0,9):
  exec(f"h_p{player}_c1_lb.bind('<<ComboboxSelected>>', partial(update_card_list, deck=deck, player={player}, card_pos=1))")
  exec(f"h_p{player}_c2_lb.bind('<<ComboboxSelected>>', partial(update_card_list, deck=deck, player={player}, card_pos=2))")
for card in range(1,6):
  exec(f"h_com_c{card}_lb.bind('<<ComboboxSelected>>', partial(update_card_list, deck=deck, player=com_player_num, card_pos={card}))")
h_num_opp_lb.bind('<<ComboboxSelected>>', partial(update_num_opp, deck=deck))

# Run GUI
h_root.mainloop()
