#include "Calculator.h"
#include <iostream>
#include <fstream>
#include <set>
#include <string>
#include <vector>
#include <queue>
#include <algorithm>
#include <functional>
#include <cstdlib>
#include <ctime>
using namespace std;

/* defines and global constants */
#define DEBUG 0

const char *inFileName  = "input.txt";
const char *outFileName = "calcService.txt";
const char *resultsFileName = "calcResults.txt";
const char *percentFileName = "calcPercents.dat";
const int MAX_PLAYERS = 9;
const char* const INT_TO_STR[] = {
    "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "10C", "JC", "QC", "KC", "AC",
    "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "10D", "JD", "QD", "KD", "AD",
    "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "10H", "JH", "QH", "KH", "AH",
    "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "10S", "JS", "QS", "KS", "AS" };

int main()
{
    int numRuns, numPlayers, cardsPicked = 0, remainingCards;
    int winCount = 0, tieCount = 0, lossCount = 0, calcPercentages;
    bool runSim = false; 
    Player playerInit[MAX_PLAYERS];
    Board boardInit;
    Card deck[52];
    set<int> pickedCardValues;
    float *winPercent, *tiePercent, *lossPercent;
    ifstream inFile;
    ofstream outFile;
    
    // Seed random num generator
    srand((unsigned int)time(NULL));

    inFile.open(inFileName, ios::in);
    if (!inFile)
    {
        cerr << "Failed to open input file \"" << inFileName << "\", exiting program\n";
        exit(EXIT_FAILURE);
    }    

    // Reading sim settings into a template structure
    ReadSimInfo(inFile, playerInit, boardInit, numRuns, numPlayers, calcPercentages, pickedCardValues, cardsPicked);

    // Create arrays for percentage histories
    winPercent = new float[numRuns] {0.};
    tiePercent = new float[numRuns] {0.};
    lossPercent = new float[numRuns] {0.};

    // Create deck with only the availble cards that haven't been fixed
    remainingCards = 52 - cardsPicked;
    for (int i = 0, index = 0; i < 52; ++i)
    {
        // Check if card is already used by the fixed cards
        if (pickedCardValues.find(i) == pickedCardValues.end())
        {
            // Card wasn't in pre-picked set so add it to availabel deck
            deck[index].setIntValue(i);
            ++index;
        }
    }
        
    // Run the monte-carlo trials to estimate percentages       
    for (int handNum = 0; handNum < numRuns; ++handNum)
    {
        Player player[MAX_PLAYERS];
        Board board;
        Card hand[7];
        HandStatus playerHandStatus[9];
        bool possibleTie;
        HandOutcome handOutcome;
        float denom;
            

        // Initialize variables
        possibleTie = false;
        handOutcome = HandOutcome::NOT_SET;
        denom = 1 / ((float)handNum + 1.f);
        /*
        for (int i = 0; i < numPlayers; ++i)
            playerHandStatus[i].reset(); */

        // Shuffle remaining deck
        ShuffleCards(deck, remainingCards);

        // Assign random cards to players and board as required
        AssignCards(player, playerInit, board, boardInit, deck, numPlayers);
#if DEBUG
        cout << "\n\nFor hand#" << handNum << ":\n";
        cout << "Players Cards:\n";
        for (int i = 0; i < numPlayers; ++i)
            cout << "\tPlayer #" << i << " cards = (" << INT_TO_STR[player[i].cards[0].getIntValue()] << ", "
            << INT_TO_STR[player[i].cards[1].getIntValue()] << ")\n";
        cout << "Board Cards:\n";
        cout << "\tBoard cards = (" << INT_TO_STR[board.cards[0].getIntValue()] << ", "
            << INT_TO_STR[board.cards[1].getIntValue()] << ", "
            << INT_TO_STR[board.cards[2].getIntValue()] << ", "
            << INT_TO_STR[board.cards[3].getIntValue()] << ", "
            << INT_TO_STR[board.cards[4].getIntValue()] << ")\n\n";
#endif
            
        // Copy board cards into each players first 5 cards of 7 card hand
        hand[0] = board.cards[0]; 
        hand[1] = board.cards[1];
        hand[2] = board.cards[2];
        hand[3] = board.cards[3];
        hand[4] = board.cards[4];

        // Set user's final 2 cards of hand and rank hand
        hand[5] = player[0].cards[0];
        hand[6] = player[0].cards[1];
        setHandStatus(hand, playerHandStatus[0]);

        // Rank opponents hands as needed
        for (int i = 1; i < numPlayers; ++i)
        {
            // Set opponent's final 2 cards of hand and rank hand
            hand[5] = player[i].cards[0];
            hand[6] = player[i].cards[1];
            setHandStatus(hand, playerHandStatus[i]);
            // Check if player lost
            if (playerHandStatus[i].rank > playerHandStatus[0].rank)
            {
                // Player lost go to next hand
                ++lossCount;
                if (calcPercentages)
                {
                    winPercent[handNum]  = winCount  * denom;
                    tiePercent[handNum]  = tieCount  * denom;
                    lossPercent[handNum] = lossCount * denom;
                }
                handOutcome = HandOutcome::LOST;
#if DEBUG
                cout << "Player lost to opponent #" << i << "\n";
                cout << "\tPlayer Hand Status:   rank = " << static_cast<int>(playerHandStatus[0].rank) << ", kickers = ("
                    << playerHandStatus[0].kickers[0] << ", "
                    << playerHandStatus[0].kickers[1] << ", "
                    << playerHandStatus[0].kickers[2] << ", "
                    << playerHandStatus[0].kickers[3] << ", "
                    << playerHandStatus[0].kickers[4] << ")\n";
                cout << "\tOpponent Hand Status: rank = " << static_cast<int>(playerHandStatus[i].rank) << ", kickers = ("
                    << playerHandStatus[i].kickers[0] << ", "
                    << playerHandStatus[i].kickers[1] << ", "
                    << playerHandStatus[i].kickers[2] << ", "
                    << playerHandStatus[i].kickers[3] << ", "
                    << playerHandStatus[i].kickers[4] << ")\n";
#endif
                break;
            }
            // If tied check for a tie-break loss
            else if (playerHandStatus[i].rank == playerHandStatus[0].rank)
            {
                // Check tie-breaker
                if (PlayerTieLost(playerHandStatus[0], playerHandStatus[i]))
                {
                    // Player lost go to next hand
                    ++lossCount;
                    if (calcPercentages)
                    {
                        winPercent[handNum]  = winCount  * denom;
                        tiePercent[handNum]  = tieCount  * denom;
                        lossPercent[handNum] = lossCount * denom;
                    }
                    handOutcome = HandOutcome::LOST;
#if DEBUG
                    cout << "Player lost to opponent #" << i << "\n";
                    cout << "\tPlayer Hand Status:   rank = " << static_cast<int>(playerHandStatus[0].rank) << ", kickers = ("
                        << playerHandStatus[0].kickers[0] << ", "
                        << playerHandStatus[0].kickers[1] << ", "
                        << playerHandStatus[0].kickers[2] << ", "
                        << playerHandStatus[0].kickers[3] << ", "
                        << playerHandStatus[0].kickers[4] << ")\n";
                    cout << "\tOpponent Hand Status: rank = " << static_cast<int>(playerHandStatus[i].rank) << ", kickers = ("
                        << playerHandStatus[i].kickers[0] << ", "
                        << playerHandStatus[i].kickers[1] << ", "
                        << playerHandStatus[i].kickers[2] << ", "
                        << playerHandStatus[i].kickers[3] << ", "
                        << playerHandStatus[i].kickers[4] << ")\n";
#endif
                    break;
                }
                else
                {
                    possibleTie = true;
                }
            }
        }
        // If user already lost, then continue to next trial
        if (handOutcome == HandOutcome::LOST)
        {
            continue;
        }
            
        // If a possible tie determine win or tie
        if (possibleTie)
        {
            // Loop over opponents and further process tie-breaks
            for (int i = 1; i < numPlayers; ++i)
            {
                // Check if opponent is tied with user
                if (playerHandStatus[i].rank == playerHandStatus[0].rank)
                {
                    // User must win all tie breaks to win the hand or else its a tie,
                    // So if user ties any one player the outcome must be a tie, because
                    // we already checked any tie-break losses above
                    if (!PlayerTieWon(playerHandStatus[0], playerHandStatus[i]))
                    {
                        // Player tied at least one other player, so end result must be tie
                        handOutcome = HandOutcome::TIE;
#if DEBUG
                        cout << "Player Tied\n";
                        cout << "\tPlayer Hand Status:      rank = " << static_cast<int>(playerHandStatus[0].rank) << ", kickers = ("
                            << playerHandStatus[0].kickers[0] << ", "
                            << playerHandStatus[0].kickers[1] << ", "
                            << playerHandStatus[0].kickers[2] << ", "
                            << playerHandStatus[0].kickers[3] << ", "
                            << playerHandStatus[0].kickers[4] << ")\n";
                        for (int o = 1; o < numPlayers; ++o)
                        {
                            cout << "\tOpponent #" << o << " Hand Status: rank = " << static_cast<int>(playerHandStatus[o].rank) << ", kickers = ("
                                << playerHandStatus[o].kickers[0] << ", "
                                << playerHandStatus[o].kickers[1] << ", "
                                << playerHandStatus[o].kickers[2] << ", "
                                << playerHandStatus[o].kickers[3] << ", "
                                << playerHandStatus[o].kickers[4] << ")\n";
                        }
#endif
                        ++tieCount;
                        if (calcPercentages)
                        {
                            winPercent[handNum] = winCount * denom;
                            tiePercent[handNum] = tieCount * denom;
                            lossPercent[handNum] = lossCount * denom;
                        }                            
                        break;
                    }
                }
            }
            // If uesr didn't tie anyone opponent, they must have won
            if (handOutcome != HandOutcome::TIE)
            {
                // Player Won
                handOutcome = HandOutcome::WON;
#if DEBUG
                cout << "Player Won\n";
                cout << "\tPlayer Hand Status:      rank = " << static_cast<int>(playerHandStatus[0].rank) << ", kickers = ("
                    << playerHandStatus[0].kickers[0] << ", "
                    << playerHandStatus[0].kickers[1] << ", "
                    << playerHandStatus[0].kickers[2] << ", "
                    << playerHandStatus[0].kickers[3] << ", "
                    << playerHandStatus[0].kickers[4] << ")\n";
                for (int o = 1; o < numPlayers; ++o)
                {
                    cout << "\tOpponent #" << o << " Hand Status: rank = " << static_cast<int>(playerHandStatus[o].rank) << ", kickers = ("
                        << playerHandStatus[o].kickers[0] << ", "
                        << playerHandStatus[o].kickers[1] << ", "
                        << playerHandStatus[o].kickers[2] << ", "
                        << playerHandStatus[o].kickers[3] << ", "
                        << playerHandStatus[o].kickers[4] << ")\n";
                }
#endif
                ++winCount;
                if (calcPercentages)
                {
                    winPercent[handNum] = winCount * denom;
                    tiePercent[handNum] = tieCount * denom;
                    lossPercent[handNum] = lossCount * denom;
                }
            }
        }
        // Didn't tie or lose, so must have won
        else
        {
            // Player Won
            handOutcome = HandOutcome::WON;
#if DEBUG
            cout << "Player Won\n";
            cout << "\tPlayer Hand Status:      rank = " << static_cast<int>(playerHandStatus[0].rank) << ", kickers = ("
                << playerHandStatus[0].kickers[0] << ", "
                << playerHandStatus[0].kickers[1] << ", "
                << playerHandStatus[0].kickers[2] << ", "
                << playerHandStatus[0].kickers[3] << ", "
                << playerHandStatus[0].kickers[4] << ")\n";
            for (int o = 1; o < numPlayers; ++o)
            {
                cout << "\tOpponent #" << o << " Hand Status: rank = " << static_cast<int>(playerHandStatus[o].rank) << ", kickers = ("
                    << playerHandStatus[o].kickers[0] << ", "
                    << playerHandStatus[o].kickers[1] << ", "
                    << playerHandStatus[o].kickers[2] << ", "
                    << playerHandStatus[o].kickers[3] << ", "
                    << playerHandStatus[o].kickers[4] << ")\n";
            }
#endif
            ++winCount;
            if (calcPercentages)
            {
                winPercent[handNum]  = winCount  * denom;
                tiePercent[handNum]  = tieCount  * denom;
                lossPercent[handNum] = lossCount * denom;
            }
        }
    } // end for (int handNum...

    // Write final percentage resluts to results file
    outFile.open(resultsFileName, ios::out);
    if (!outFile)
    {
        cerr << "Failed to open output file \"" << resultsFileName << "\", exiting program\n";
        exit(EXIT_FAILURE);
    }
    outFile << (double)winCount / numRuns << "\n";
    outFile << (double)tieCount / numRuns << "\n";
    outFile << (double)lossCount / numRuns << "\n";
    outFile.close();

    // Write optional percentage files
    if (calcPercentages)
    {
        outFile.open(percentFileName, ios::out | ios::binary);
        if (!outFile)
        {
            cerr << "Failed to open output file \"" << percentFileName << "\", exiting program\n";
            exit(EXIT_FAILURE);
        }
        for (int i=0; i<numRuns; ++i)
            outFile.write(reinterpret_cast<const char *>(&winPercent[i]), sizeof(float));
        for (int i = 0; i < numRuns; ++i)
            outFile.write(reinterpret_cast<const char*>(&tiePercent[i]), sizeof(float));
        for (int i = 0; i < numRuns; ++i)
            outFile.write(reinterpret_cast<const char*>(&lossPercent[i]), sizeof(float));
        outFile.close();
    }
    return 0;
}


/******************************************************************************
* name = ReadSimInfo
* parameters:
*   inFile     = ifstream objectect representing open file with simulation settings info
*   playerInit = pointer to player struct array which holds the card settings of each player
*   boardInit  = reference to board struct which holds the card settings of the community cards
*   numRuns    = reference to number of trials to run
*   numPlayers = reference to total number of players including user
*   calcPercentages = reference to flag to calculate percentage histories
*   pickedCardValues = reference to a set of integers representing the card values already picked from deck
*   cardsPicked = reference to int that holds the total number of fixed cards already picked
* return:
*   none
*
* Function will read the input simulation config file which has info on the # of trials
* to run, the total # of players in game, whether to calcluate percentage histories,
* which cards are fixed and which are randomly assigned. This info will be read in
* to the proper variables and used in the simulation
******************************************************************************/
void ReadSimInfo(ifstream &inFile, Player *playerInit, Board &boardInit, int &numRuns,
    int &numPlayers, int &calcPercentages, set<int> &pickedCardValues, int &cardsPicked)
{
    inFile >> numRuns >> numPlayers >> calcPercentages;
    // Loop over all players
    for (int i = 0; i < numPlayers; ++i)
    {
        // Loop over each card of player
        for (int j = 0; j < 2; ++j)
        {
            int c;
            inFile >> c;
            // If not random add to picked card set and increment cardsPicked
            if (c != RAND_CARD_VALUE)
            {
                ++cardsPicked;
                pickedCardValues.insert(c);
                playerInit[i].cards[j].value = c % 13;
                playerInit[i].cards[j].suit = c / 13;
            }
        }
    }
    // Loop over community cards
    for (int i = 0; i < 5; ++i)
    {
        int c;
        inFile >> c;
        // If not random add to picked card set and increment cardsPicked
        if (c != RAND_CARD_VALUE)
        {
            ++cardsPicked;
            pickedCardValues.insert(c);
            boardInit.cards[i].value = c % 13;
            boardInit.cards[i].suit = c / 13;
        }
    }
    inFile.close();
    return;
}


/******************************************************************************
* name = _swapCards
* parameters:
*   c1 = pointer to a Card struct
*   c2 = pointer to a Card struct
* return:
*   none
*
* Function will swap the value and suit of the 2 card pointers passed int, this
* is a helper function for the shuffling algorithm
******************************************************************************/
inline void _swapCards(Card *c1, Card *c2)
{
    int v = c1->value, s = c1->suit;
    c1->value = c2->value;
    c1->suit = c2->suit;
    c2->value = v;
    c2->suit = s;
    return;
}


/******************************************************************************
* name = ShuffleCards
* parameters:
*   deck           = pointer to an array of Card structs
*   remainingCards = # of available cards in deck
* return:
*   none
*
* Function will shuffle the card deck using the Fisher-Yates algorithm
******************************************************************************/
void ShuffleCards(Card *deck, int remainingCards)
{
    for (int i = remainingCards - 1; i > 0; --i)
    {
        // Pick random j in range 0 to i
        int j = rand() % (i + 1);
        // if different swap cards
        if (i != j)
            _swapCards(deck + i, deck + j);
    }
    return;
}


/******************************************************************************
* name = AssignCards
* parameters:
*   player     = pointer to Player struct array which holds the card info for the current hand
*   playerInit = const pointer to player struct array which holds the card settings of each player
*   board      = reference to Board struct which holds the card info for the cumminity cards for the current hand
*   boardInit  = const reference to Board struct which holds the card settings of the community cards
*   deck       = const pointer to array of Card structs representing the shuffled deck
*   numPlayers = total number of players including user
* return:
*   none
*
* Function will fill in all the cards for players and community board which are
* marked as random, cards will be assigned sequentially from a shuffled deck
******************************************************************************/
void AssignCards(Player *player, const Player *playerInit, Board &board, const Board &boardInit, const Card *deck, int numPlayers)
{
    int iDeck = 0;
    // Loop over all players
    for (int i = 0; i < numPlayers; ++i)
    {
        // Loop over all player cards
        for (int j = 0; j < 2; ++j)
        {
            // If card is set as random then assign it from deck and increment deck position
            if (playerInit[i].cards[j].value == RAND_CARD_VALUE)
            {
                player[i].cards[j].setValueSuit(deck[iDeck].value, deck[iDeck].suit);
                ++iDeck;
            }
            // Else set card from fixed card settings
            else
                player[i].cards[j].setValueSuit(playerInit[i].cards[j].value, playerInit[i].cards[j].suit);
        }        
    }
    // Loop over all community board cards
    for (int i = 0; i < 5; ++i)
    {
        // If card is set as random then assign it from deck and increment deck position
        if (boardInit.cards[i].value == RAND_CARD_VALUE)
        {
            board.cards[i].setValueSuit(deck[iDeck].value, deck[iDeck].suit);
            ++iDeck;
        }
        // Else set card from fixed card settings
        else
            board.cards[i].setValueSuit(boardInit.cards[i].value, boardInit.cards[i].suit);
    }
    return;
}


/******************************************************************************
* name = _CompareKickersLost
* parameters:
*   k1           = pointer to array of int kickers which serve as tie breaker values
*   k2           = pointer to array of int kickers which serve as tie breaker values
*   numToCompare = number of kickers to compare
* return:
*   returns boolean true if user lost tie-break otherwise false
*
* Function is a helper function which will compare tie-breaker values in the 
* case of a tie to check for a loss only. If at any point k1[i] < k2[i] then hand
* representing k1 has lost, if at any point k1[i] > k2[i] then hand representing
* k1 has not lost, if all kickers are same then k1 has not lost either
******************************************************************************/
bool _CompareKickersLost(const int *k1, const int *k2, int numToCompare)
{
    for (int i = 0; i < numToCompare; ++i)
    {
        if (k1[i] < k2[i])
            return true;
        else if (k1[i] > k2[i])
            return false;
    }
    return false;
}


/******************************************************************************
* name = PlayerTieLost
* parameters:
*   playerHandStatus   = const reference to users HandStatus struct
*   opponentHandStatus = const reference to opponents HandStatus struct
* return:
*   returns boolean true if user lost tie-break otherwise false
*
* Function will determine if the user has lost a tie-breaker by comparing the
* relevant kickers which depend on the hand rank
******************************************************************************/
bool PlayerTieLost(const HandStatus &playerHandStatus, const HandStatus &opponentHandStatus)
{
    // Opponents are assumed to have identical hand rank, so compare kickers to determine if lost
    switch (playerHandStatus.rank)
    {
    case HandRank::ROYAL_FLUSH:
        // No tie break possible, must be tie
        return false;
    case HandRank::STRAIGHT_FLUSH:
        // Compare first kicker only, high card of straight
        return _CompareKickersLost(playerHandStatus.kickers, opponentHandStatus.kickers, 1);
    case HandRank::FOUR_OF_KIND:
        // Compare first 2 kickers, value of 4 of kind & 5th card kicker
        return _CompareKickersLost(playerHandStatus.kickers, opponentHandStatus.kickers, 2);        
    case HandRank::FULL_HOUSE:
        // Compare first 2 kickers, value of 3 of a kind & value of pair
        return _CompareKickersLost(playerHandStatus.kickers, opponentHandStatus.kickers, 2);
    case HandRank::FLUSH:
        // Compare all 5 kickers, 5 flush cards
        return _CompareKickersLost(playerHandStatus.kickers, opponentHandStatus.kickers, 5);
    case HandRank::STRAIGHT:
        // Compare first kicker, high card of straight
        return _CompareKickersLost(playerHandStatus.kickers, opponentHandStatus.kickers, 1);
    case HandRank::THREE_OF_KIND:
        // Compare first 3 kickers, 3 of kind value, and 2 kickers
        return _CompareKickersLost(playerHandStatus.kickers, opponentHandStatus.kickers, 3);
    case HandRank::TWO_PAIR:
        // Compare first 3 kickers, 1st pair value, 2nd pair value, and 1 kicker
        return _CompareKickersLost(playerHandStatus.kickers, opponentHandStatus.kickers, 3);
    case HandRank::ONE_PAIR:
        // Compare first 4 kickers, pair value, 4 kickers
        return _CompareKickersLost(playerHandStatus.kickers, opponentHandStatus.kickers, 4);
    case HandRank::HIGH_CARD:
        // Compare all 5 kickers
        return _CompareKickersLost(playerHandStatus.kickers, opponentHandStatus.kickers, 5);
    default:
        cerr << "Bad HandRank detected in PlayerTieLost()\n";
        return false;
    }
}


/******************************************************************************
* name = _CompareKickersWon
* parameters:
*   k1           = pointer to array of int kickers which serve as tie breaker values
*   k2           = pointer to array of int kickers which serve as tie breaker values
*   numToCompare = number of kickers to compare
* return:
*   returns boolean true if user won tie-break otherwise false
*
* Function is a helper function which will compare tie-breaker values in the
* case of a tie to check for a win only. If at any point k1[i] > k2[i] then hand
* representing k1 has won, if at any point k1[i] < k2[i] then hand representing
* k1 has not won, if all kickers are same then k1 has not won either
******************************************************************************/
bool _CompareKickersWon(const int *k1, const int *k2, int numToCompare)
{
    for (int i = 0; i < numToCompare; ++i)
    {
        if (k1[i] > k2[i])
            return true;
        else if (k1[i] < k2[i])
            return false;
    }
    return false;
}


/******************************************************************************
* name = PlayerTieWon
* parameters:
*   playerHandStatus   = const reference to users HandStatus struct
*   opponentHandStatus = const reference to opponents HandStatus struct
* return:
*   returns boolean true if user won tie-break otherwise false
*
* Function will determine if the user has won a tie-breaker by comparing the
* relevant kickers which depend on the hand rank
******************************************************************************/
bool PlayerTieWon(const HandStatus &playerHandStatus, const HandStatus &opponentHandStatus)
{
    // Opponents are assumed to have identical hand rank, so compare kickers to determine if won
    switch (playerHandStatus.rank)
    {
    case HandRank::ROYAL_FLUSH:
        // No tie break possible, must be tie
        return false;
    case HandRank::STRAIGHT_FLUSH:
        // Compare first kicker only, high card of straight
        return _CompareKickersWon(playerHandStatus.kickers, opponentHandStatus.kickers, 1);
    case HandRank::FOUR_OF_KIND:
        // Compare first 2 kickers, value of 4 of kind & 5th card kicker
        return _CompareKickersWon(playerHandStatus.kickers, opponentHandStatus.kickers, 2);
    case HandRank::FULL_HOUSE:
        // Compare first 2 kickers, value of 3 of a kind & value of pair
        return _CompareKickersWon(playerHandStatus.kickers, opponentHandStatus.kickers, 2);
    case HandRank::FLUSH:
        // Compare all 5 kickers, 5 flush cards
        return _CompareKickersWon(playerHandStatus.kickers, opponentHandStatus.kickers, 5);
    case HandRank::STRAIGHT:
        // Compare first kicker, high card of straight
        return _CompareKickersWon(playerHandStatus.kickers, opponentHandStatus.kickers, 1);
    case HandRank::THREE_OF_KIND:
        // Compare first 3 kickers, 3 of kind value, and 2 kickers
        return _CompareKickersWon(playerHandStatus.kickers, opponentHandStatus.kickers, 3);
    case HandRank::TWO_PAIR:
        // Compare first 3 kickers, 1st pair value, 2nd pair value, and 1 kicker
        return _CompareKickersWon(playerHandStatus.kickers, opponentHandStatus.kickers, 3);
    case HandRank::ONE_PAIR:
        // Compare first 4 kickers, pair value, 4 kickers
        return _CompareKickersWon(playerHandStatus.kickers, opponentHandStatus.kickers, 4);
    case HandRank::HIGH_CARD:
        // Compare all 5 kickers
        return _CompareKickersWon(playerHandStatus.kickers, opponentHandStatus.kickers, 5);
    default:
        cerr << "Bad HandRank detected in PlayerTieLost()\n";
        return false;
    }
}


/******************************************************************************
* name = _containsStraight
* parameters:
*   uValues = reference to vector of int representing the unique & sorted card values of a hand
*   kicker  = reference to int representing the single kicker if a straight is made
* return:
*   returns boolean true if straight is detected otherwise false
*
* Function is a helper function to determine whether a players hand contains a
* straight, if it does the single kicker is assigned
******************************************************************************/
bool _containsStraight(vector<int> &uValues, int &kicker)
{
    // Look for 5 card consecutive sequences starting with highest card
    // unique vector of values is sorted in descending order
    int numToCheck, i, j, startVal;

    // If ace is in vValues add it as the lowest card too
    if (uValues[0] == 12)
        uValues.push_back(-1);
    numToCheck = uValues.size() - 4;
    i = 0;
    // Loop through sorted unique values to check for straight
    while (i < numToCheck)
    {
        // Get starting card
        startVal = uValues[i];
        // Check next 4 cards to see if they are consecutive
        for (j = 1; j < 5; ++j)
        {
            if (uValues[i + j] != startVal - j)
                break;
            if (j == 4)
            {
                kicker = startVal;
                return true;
            }
        }
        // If not a straight at that starting point, resume checking at point where it failed
        i += j;        
    }
    return false;
}


/******************************************************************************
* name = _isStraight
* parameters:
*   hand       = pointer to an array of Card structs representing the players hand
*   handStatus = reference to HandStatus struct representing players hand status
* return:
*   returns boolean true if player has a straight otherwise false
*
* Function is a helper function to determine whether a players hand has a 
* straight
******************************************************************************/
bool _isStraight(const Card *hand, HandStatus &handStatus)
{
    vector<int> uValues;
    // Put only unique values in a vector
    for (int i = 0; i < 7; ++i)
    {   if (find(uValues.begin(), uValues.end(), hand[i].value) == uValues.end())
        {   // Element not found in unique value list
            uValues.push_back(hand[i].value);
        }            
    }
    // Sort values in descending order
    sort(uValues.begin(), uValues.end(), greater<int>());
    // Check if unique sorted values contain a straight
    if (_containsStraight(uValues, handStatus.kickers[0]))
    {
        handStatus.rank = HandRank::STRAIGHT;
        return true;
    }
    return false;
}


/******************************************************************************
* name = setHandStatus
* parameters:
*   hand       = pointer to an array of Card structs representing the players hand
*   handStatus = reference to HandStatus struct representing players hand status
* return:
*   none
*
* Function will take a players 7 card hand and set the rank of the hand and the
* tie-breaking kickers and store info in the handStatus struct
******************************************************************************/
void setHandStatus(const Card *hand, HandStatus &handStatus)
{
    // Check for Royal Flush, can also check for Straight Flush & Flush

    // Put same suit cards in there own vector
    vector<int> suitedValues[4];
    // Put each card value in containers separated by suit
    for (int i = 0; i < 7; ++i)
    {
        switch (hand[i].suit)
        {
        case 0:
            suitedValues[0].push_back(hand[i].value);
            break;
        case 1:
            suitedValues[1].push_back(hand[i].value);
            break;
        case 2:
            suitedValues[2].push_back(hand[i].value);
            break;
        case 3:
            suitedValues[3].push_back(hand[i].value);
            break;
#if DEBUG
        default:
            cerr << "Bad suit detected in _isRoyalFlush()\n";
            break;
#endif
        }
    }
    // Check lengths of each vector, if at least 5 then player has at least a flush
    // possibly straight flush or royal flush
    for (int suit = 0; suit < 4; ++suit)
    {
        if (suitedValues[suit].size() >= 5)
        {
            // Sort the values in descending order
            sort(suitedValues[suit].begin(), suitedValues[suit].end(), greater<int>());
            // Check for royal flush
            if (suitedValues[suit][0] == 12 && suitedValues[suit][1] == 11 && suitedValues[suit][2] == 10
                && suitedValues[suit][3] == 9 && suitedValues[suit][4] == 8)
            {
                handStatus.rank = HandRank::ROYAL_FLUSH;
                return;
            }
            // Check for straight flush
            else if (_containsStraight(suitedValues[suit], handStatus.kickers[0]))
            {
                handStatus.rank = HandRank::STRAIGHT_FLUSH;
                return;
            }
            // Player has flush, assign handStatus
            else
            {
                handStatus.rank = HandRank::FLUSH;
                for (int i = 0; i < 5; ++i)
                    handStatus.kickers[i] = suitedValues[suit][i];
            }
        }
    }
        
    // Check for 4 of a kind, 3 of a kind, fullhouse, 2-pair, 1-pair, and High Card
    int valueCounts[] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    int max_count = 0, max_count_val = -1, next_max_count = 0,  next_max_count_val = -1;
    priority_queue<int> pqValues;

    // Get the count of each value in hand and place values in a max priority queue
    for (int i = 0; i < 7; ++i)
    {
        ++valueCounts[hand[i].value];
        pqValues.push(hand[i].value);
    }
    // Determine the 2 highest frequency cards, in case of tie of frequency take card with highest value
    for (int i = 0; i < 13; ++i)
    {
        if (valueCounts[i] >= max_count)
        {
            // This is the highest or same as highest frequency card but with higher value, the previous highest gets pushed down to next highest
            next_max_count = max_count;
            next_max_count_val = max_count_val;
            max_count = valueCounts[i];
            max_count_val = i;
        }
        else if (valueCounts[i] >= next_max_count)
        {
            // This is the next highest or same as next highest frequency card but with higher value, pevious next highest is gone
            next_max_count = valueCounts[i];
            next_max_count_val = i;
        }
    }

    // Process hand based on the 2 highest counts
    // Check for 4 of a kind
    if (max_count == 4)
    {
        // 4 of a kind, 2 kickers, value of 4 of a kind and value of highest card that isn't the 4 of a kind value
        handStatus.rank = HandRank::FOUR_OF_KIND;
        handStatus.kickers[0] = max_count_val;
        // Assign highest value which is not the 4 of a kind value
        int numAssigned = 0;
        while (numAssigned < 1)
        {
            if (pqValues.top() != max_count_val)
            {
                ++numAssigned;
                handStatus.kickers[numAssigned] = pqValues.top();
            }
            pqValues.pop();
        }
        return;
    }
    // Check for Full-house
    if (max_count == 3)
    {
        // Check for pair to make full-house
        if (next_max_count >= 2)
        {
            // Full-House, 2 kickers, value of highest 3 of a kind and value of highest pair
            handStatus.rank = HandRank::FULL_HOUSE;
            handStatus.kickers[0] = max_count_val;
            handStatus.kickers[1] = next_max_count_val;
            return;
        }
    }
    // Check for Flush
    if (handStatus.rank == HandRank::FLUSH)
    {
        return;
    }
    // Check for Straight
    if (_isStraight(hand, handStatus))
    {
        return;
    }
    // Check for 3 of a kind
    if (max_count == 3)
    {
        // 3 of a kind, 3 kickers, value of 3 of a kind and values of 2 highest cards that isn't the highest 3 of a kind
        handStatus.rank = HandRank::THREE_OF_KIND;
        handStatus.kickers[0] = max_count_val;
        int numAssigned = 0;
        while (numAssigned < 2)
        {
            if (pqValues.top() != max_count_val)
            {
                ++numAssigned;
                handStatus.kickers[numAssigned] = pqValues.top();
            }
            pqValues.pop();
        }
        return;
    }
    // Check for 2-pair or 1-pair
    if (max_count == 2)
    {
        // Check for 2nd pair
        if (next_max_count == 2)
        {
            // 2-pair, 3 kickers, values of 2 highest pairs and value of highest card that isn't the 2 pairs
            handStatus.rank = HandRank::TWO_PAIR;
            handStatus.kickers[0] = max_count_val;
            handStatus.kickers[1] = next_max_count_val;
            int numAssigned = 0;
            while (numAssigned < 1)
            {
                if (pqValues.top() != max_count_val && pqValues.top() != next_max_count_val)
                {
                    ++numAssigned;
                    handStatus.kickers[numAssigned + 1] = pqValues.top();
                }
                pqValues.pop();
            }
        }
        else
        {
            // One-pair, 4 kickers, value of highest pair and values of 3 highest cards that aren't the highest pair value
            handStatus.rank = HandRank::ONE_PAIR;
            handStatus.kickers[0] = max_count_val;
            int numAssigned = 0;
            while (numAssigned < 3)
            {
                if (pqValues.top() != max_count_val)
                {
                    ++numAssigned;
                    handStatus.kickers[numAssigned] = pqValues.top();
                }
                pqValues.pop();
            }
        }
        return;
    }
    // max_count == 1 -> High card, 5 kickers, all 5 highest cards
    handStatus.rank = HandRank::HIGH_CARD;
    int numAssigned = 0;
    while (numAssigned < 5)
    {
        handStatus.kickers[numAssigned] = pqValues.top();
        pqValues.pop();
        ++numAssigned;
    }
    return;
}
