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
  # Get Players previously selected card
  prev_card_str = eval(f"p{player}_c{card_pos}_lbl.get()")
  # Get Players newly selected card
  new_card_str = eval(f"p{player}_c{card_pos}.get()")
  # Make available in deck if necessary
  if not (prev_card_str == '?' or prev_card_str == new_card_str):
    # There was a previous card and the new selection is different, so free previous
    mark_used(deck, prev_card_str, False)
  # Set players card in display label
  eval(f"p{player}_c{card_pos}_lbl.set(new_card_str)")
  # Mark new card choice as used
  mark_used(deck, new_card_str, True)
  # Update all card lists
  update_all_card_lists(deck)
  # DEBUG
  print(f"player {player} selected {new_card_str} for card#{card_pos}")

def toggle_fixed_cards(*args, player, card_pos):
  if player == -1:
    # Community cards toggled
    state = eval(f"com_c{card_pos}_fix.get()")
    prefix = "com"
  else:
    state = eval(f"p{player}_c{card_pos}_fix.get()")
    prefix = f"p{player}"
  if state == "1":
    # Make Drop-down list appear
    x = eval(f"{prefix}_start[0]") + (card_pos - 1) * card_x_offset
    y = eval(f"{prefix}_start[1] + card_y_cb_offset")
    eval(f"h_{prefix}_c{card_pos}_lb.place(x=x,y=y)")
  else:
    card_str = eval(f"{prefix}_c{card_pos}_lbl.get()")
    # Make fixed card available in deck if necessary
    if not card_str == '?':
      mark_used(deck, card_str, False)
    # Set card label to random
    eval(f"{prefix}_c{card_pos}_lbl.set('?')")
    # Update all card lists
    update_all_card_lists(deck)
    # Make Drop-down list disappear
    eval(f"h_{prefix}_c{card_pos}_lb.place_forget()")

def update_all_card_lists(deck):
  values = get_deck_values(deck)
  h_p6_c1_lb['values'] = values
  h_p6_c2_lb['values'] = values
#------------------------------------------------------------------------------



# GUI Settings --------------------------------
main_title = "Hold'em Odds"
main_window_width = 1200
main_window_height = 600
root_frame_padding = "3 3 3 3"
label_relief_default = 'ridge'
label_padding_default = "5 5 5 5"
player_label_width = 21
player_label_color = "#99ffff"
user_label_color = "#66ff66"
option_label_color = "#ffff66"
trials_label_width = 12
community_label_width = 62
card_frame_width = 100
card_frame_height = 50
card_padding_default = "3 3 3 3"
card_label_width = 8
cards_relief = "sunken"
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
# ---------------------------------------------


# Main window
h_root = Tk()
h_root.title(main_title)
h_root.geometry(f"{main_window_width}x{main_window_height}")
h_root.resizable(False, False)
h_root_frame = ttk.Frame(h_root, padding = root_frame_padding, width=main_window_width, height=main_window_height)

# Global GUI variables ------------------------
deck = create_deck([])
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
  exec(f"h_p{player}_label = ttk.Label(h_root_frame, text=player_label_str,"
  f"relief=label_relief_default, width=player_label_width,"
  f"padding=label_padding_default, background=bg_color, anchor='center')")
  # Card display labels
  exec(f"h_p{player}_c1_lbl = ttk.Label(h_root_frame, textvariable=p{player}_c1_lbl,"
  f"relief=cards_relief, width=card_label_width, background='#fff',"
  f"padding=card_padding_default)")
  exec(f"h_p{player}_c2_lbl = ttk.Label(h_root_frame, textvariable=p{player}_c2_lbl,"
  f"relief=cards_relief, width=card_label_width, background='#fff',"
  f"padding=card_padding_default)")
  # Checkboxes to toggle manual selection
  exec(f"h_p{player}_c1_cb = ttk.Checkbutton(h_root_frame, text='Fix',"
  f"variable=p{player}_c1_fix, command=partial(toggle_fixed_cards, player={player}, card_pos=1)," f"width=card_label_width)")
  exec(f"h_p{player}_c2_cb = ttk.Checkbutton(h_root_frame, text='Fix',"
  f"variable=p{player}_c2_fix, command=partial(toggle_fixed_cards, player={player}, card_pos=2)," f"width=card_label_width)")
  # Dropdown lists to select fixed cards
  exec(f"h_p{player}_c1_lb = ttk.Combobox(h_root_frame,"
  f"textvariable=p{player}_c1, values=get_deck_values(deck), width=card_label_width)")
  exec(f"h_p{player}_c2_lb = ttk.Combobox(h_root_frame,"
  f"textvariable=p{player}_c2, values=get_deck_values(deck), width=card_label_width)")
# Community card widgets
h_com_label = ttk.Label(h_root_frame, text="Community Cards", relief=label_relief_default,
width=community_label_width, padding=label_padding_default, background=player_label_color,
anchor='center')
for card in range(1,6):
  # Card display labels
  exec(f"h_com_c{card}_lbl = ttk.Label(h_root_frame, textvariable=com_c{card}_lbl,"
  f"relief=cards_relief, width=card_label_width, background='#fff',"
  f"padding=card_padding_default)")
  # Checkboxes to toggle manual selection
  exec(f"h_com_c{card}_cb = ttk.Checkbutton(h_root_frame, text='Fix',"
  f"variable=com_c{card}_fix, command=partial(toggle_fixed_cards, player=-1, card_pos={card}),"
  f"width=card_label_width)")
  # Dropdown list to select fixed cards
  exec(f"h_com_c{card}_lb = ttk.Combobox(h_root_frame,"
  f"textvariable=com_c{card}, values=get_deck_values(deck), width=card_label_width)")
# Rest of widgets
h_trials_label = ttk.Label(h_root_frame, text="# of Trials", relief=label_relief_default,
width=trials_label_width, padding=label_padding_default, background=option_label_color)

#------------------------------------------------------------------------------

# Place widgets ---------------------------------------------------------------
h_root_frame.place(relx=0.5, rely=0.5, anchor='center')
# Player widgets
for player in range(9):
  exec(f"h_p{player}_label.place(x=p{player}_start[0], y=p{player}_start[1])")
  exec(f"h_p{player}_c1_lbl.place(x=p{player}_start[0], y=p{player}_start[1] + card_y_lbl_offset)")
  exec(f"h_p{player}_c2_lbl.place(x=p{player}_start[0] + card_x_offset, y=p{player}_start[1] + card_y_lbl_offset)")
  exec(f"h_p{player}_c1_cb.place(x=p{player}_start[0], y=p{player}_start[1] + card_y_card_offset)")
  exec(f"h_p{player}_c2_cb.place(x=p{player}_start[0] + card_x_offset, y=p{player}_start[1] + card_y_card_offset)")
  # Temporary
  exec(f"h_p{player}_c1_lb.place(x=p{player}_start[0], y=p{player}_start[1] + card_y_cb_offset)")
  exec(f"h_p{player}_c2_lb.place(x=p{player}_start[0] + card_x_offset, y=p{player}_start[1] + card_y_cb_offset)")
h_com_label.place(x=com_start[0], y=com_start[1])
for card in range(1,6):
  x = com_start[0] + (card - 1) * card_x_offset
  exec(f"h_com_c{card}_lbl.place(x=x, y=com_start[1] + card_y_lbl_offset)")
  exec(f"h_com_c{card}_cb.place(x=x, y=com_start[1] + card_y_card_offset)")
  # Temporary
  exec(f"h_com_c{card}_lb.place(x=x, y=com_start[1] + card_y_cb_offset)")
h_trials_label.place(x=20, y=550)
#------------------------------------------------------------------------------

# Key bindings
for player in range(0,9):
  exec(f"h_p{player}_c1_lb.bind('<<ComboboxSelected>>', partial(update_card_list, deck=deck, player={player}, card_pos=1))")
  exec(f"h_p{player}_c2_lb.bind('<<ComboboxSelected>>', partial(update_card_list, deck=deck, player={player}, card_pos=2))")

# Run GUI
h_root.mainloop()
