class Card:
  def __init__(self, value_in, suit_in):
    # Values are: 2->0..., 10->8, J->9, Q->10, K->11, A->12
    # Suits are: C->0, D->1, H->2, S->3
    # Value = int_value % 13, suit = int_value / 4
    card_vals = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6,
                 '9': 7, '10': 8 , 'J': 9, 'Q': 10, 'K': 11, 'A': 12}
    suit_vals = {'C': 0, 'D': 1, 'H': 2, 'S': 3}
    if isinstance(value_in, str):
      self.value = card_vals[value_in]
    else:
      self.value = value_in
    if isinstance(suit_in, str):
      self.suit = suit_vals[suit_in]
    else:
       self.suit = suit_in
    self.used = False

  def get_value(self):
    return self.value

  def get_suit(self):
    return self.suit

  def set_used(self, state):
    self.used = state

  def is_used(self):
    return self.used

  def get_int_value(self):
    return self.suit * 13 + self.value

  def get_str_value(self):
    card_strs = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    suit_strs = ['C','D','H','S']
    return f"{card_strs[self.value]} of {suit_strs[self.suit]}"
