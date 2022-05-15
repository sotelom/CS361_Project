#ifndef CALCULATOR_H
#define CALCULATOR_H

#include <fstream>
#include <set>
using namespace std;

#define RAND_CARD_VALUE 52

enum class HandRank { HIGH_CARD = 1, ONE_PAIR, TWO_PAIR, THREE_OF_KIND, STRAIGHT, FLUSH, FULL_HOUSE, FOUR_OF_KIND, STRAIGHT_FLUSH, ROYAL_FLUSH, NONE };
enum class HandOutcome { LOST, TIE, WON, NOT_SET };

struct Card {
    int value;
    int suit;
    Card() { value = RAND_CARD_VALUE; suit = RAND_CARD_VALUE; }
    Card(int iVal) { value = iVal % 13; suit = iVal / 13; }
    int getIntValue()
    {
        if (value == RAND_CARD_VALUE)
            return value;
        else
            return value + 13 * suit;
    }
    void setIntValue(int iVal) { value = iVal % 13; suit = iVal / 13; }
    void setValueSuit(int v, int s) { value = v; suit = s; }
};

struct Player {
    Card cards[2];
};

struct Board {
    Card cards[5];
};

struct HandStatus {
    HandRank rank;
    int kickers[5];
    HandStatus() { rank = HandRank::NONE; kickers[0] = kickers[1] = kickers[2] = kickers[3] = kickers[4] = -1; }
    void reset() { rank = HandRank::NONE; kickers[0] = kickers[1] = kickers[2] = kickers[3] = kickers[4] = -1; }
};

void ReadSimInfo(ifstream&, Player*, Board&, int&, int&, int&, set<int>&, int&);
void ShuffleCards(Card*, int);
void AssignCards(Player*, const Player*, Board&, const Board&, const Card*, int);
void setHandStatus(const Card*, HandStatus&);
bool PlayerTieLost(const HandStatus&, const HandStatus&);
bool PlayerTieWon(const HandStatus&, const HandStatus&);

#endif
