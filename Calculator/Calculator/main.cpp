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
#define DEBUG 1
#define RAND_CARD_VALUE 52

const char *inFileName  = "input.txt";
const char *outFileName = "calcService.txt";
const char *resultsFileName = "calcResults.txt";
const char *percentFileName = "calcPercents.dat";
const int MAX_PLAYERS = 9;
//vector<string> INT_TO_STR{
//    "2 of C", "3 of C", "4 of C", "5 of C", "6 of C", "7 of C", "8 of C", "9 of C", "10 of C", "J of C", "Q of C", "K of C", "A of C",
//    "2 of D", "3 of D", "4 of D", "5 of D", "6 of D", "7 of D", "8 of D", "9 of D", "10 of D", "J of D", "Q of D", "K of D", "A of D",
//    "2 of H", "3 of H", "4 of H", "5 of H", "6 of H", "7 of H", "8 of H", "9 of H", "10 of H", "J of H", "Q of H", "K of H", "A of H",
//    "2 of S", "3 of S", "4 of S", "5 of S", "6 of S", "7 of S", "8 of S", "9 of S", "10 of S", "J of S", "Q of S", "K of S", "A of S" };
vector<string> INT_TO_STR{
    "2C", "3C", "4C", "5C", "6C", "7C", "8C", "9C", "10C", "JC", "QC", "KC", "AC",
    "2D", "3D", "4D", "5D", "6D", "7D", "8D", "9D", "10D", "JD", "QD", "KD", "AD",
    "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "10H", "JH", "QH", "KH", "AH",
    "2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "10S", "JS", "QS", "KS", "AS" };
enum class HandRank {HIGH_CARD = 1, ONE_PAIR, TWO_PAIR, THREE_OF_KIND, STRAIGHT, FLUSH, FULL_HOUSE, FOUR_OF_KIND, STRAIGHT_FLUSH, ROYAL_FLUSH, NONE};
enum class HandOutcome {LOST = -1, TIE, WON, NOT_SET};

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
    int getIntValue(int card)
    {
        return cards[card].getIntValue();
    }
};

struct Board {
    Card cards[5];
    int getIntValue(int card)
    {
        return cards[card].getIntValue();
    }
};

struct HandStatus {
    HandStatus() { rank = HandRank::NONE; kickers[0] = kickers[1] = kickers[2] = kickers[3] = kickers[4] = -1; }
    void reset() { rank = HandRank::NONE; kickers[0] = kickers[1] = kickers[2] = kickers[3] = kickers[4] = -1; }
    HandRank rank;
    int kickers[5];
};

void ReadSimInfo(ifstream &, Player *, Board &, int &, int &, int &, set<int> &, int &);
void ShuffleCards(Card *, int);
void AssignCards(Player *, const Player *, Board &, const Board &, const Card *, int);
void setHandStatus(const Card*, HandStatus &);
bool PlayerTieLost(const HandStatus &, const HandStatus &);
bool PlayerTieWon(const HandStatus &, const HandStatus &);


int main()
{
    string line;
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
    //// Check input file for run command
    //inFile >> line;
    //if (line.compare("run") == 0)
    //{
    //    runSim = true;
    //    
    //}
    runSim = true;

    // If ready to run, run simulation
    if (runSim)
    {
        // Reading sim settings into a template structure
        ReadSimInfo(inFile, playerInit, boardInit, numRuns, numPlayers, calcPercentages, pickedCardValues, cardsPicked);
        winPercent  = new float[numRuns] {0.};
        tiePercent  = new float[numRuns] {0.};
        lossPercent = new float[numRuns] {0.};
        
        // Create remaining cards deck
        remainingCards = 52 - cardsPicked;
        for (int i = 0, index = 0; i < 52; ++i)
        {
            if (pickedCardValues.find(i) == pickedCardValues.end())
            {
                // Card wasn't in pre-picked set so add it to availabel deck
                deck[index].setIntValue(i);
                ++index;
            }
        }
        
        // Run the hands       
        for (int handNum = 0; handNum < numRuns; ++handNum)
        {
            Player player[MAX_PLAYERS];
            Board board;
            Card hand[7];
            HandStatus playerHandStatus[9];
            bool possibleTie;
            HandOutcome handOutcome;
            float denom;
            

            // Reset variables
            possibleTie = false;
            handOutcome = HandOutcome::NOT_SET;
            denom = (float)handNum + 1.f;
#if DEBUG
            for (int i = 0; i < numPlayers; ++i)
                playerHandStatus[i].reset();
#endif

            // Shuffle remaining deck
            ShuffleCards(deck, remainingCards);

            // Assign cards to players and board
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
            
            // Copy board cards into everyones first 5 cards of 7 card hand
            hand[0] = board.cards[0]; 
            hand[1] = board.cards[1];
            hand[2] = board.cards[2];
            hand[3] = board.cards[3];
            hand[4] = board.cards[4];

            // Rank user's hand
            hand[5] = player[0].cards[0];
            hand[6] = player[0].cards[1];
            setHandStatus(hand, playerHandStatus[0]);

            // Rank opponents hands
            for (int i = 1; i < numPlayers; ++i)
            {
                // Copy opponents 2 cards into 7 card hand
                hand[5] = player[i].cards[0];
                hand[6] = player[i].cards[1];
                setHandStatus(hand, playerHandStatus[i]);
                if (playerHandStatus[i].rank > playerHandStatus[0].rank)
                {
                    // Player lost go to next hand
                    ++lossCount;
                    if (calcPercentages)
                    {
                        winPercent[handNum]  = winCount  / denom;
                        tiePercent[handNum]  = tieCount  / denom;
                        lossPercent[handNum] = lossCount / denom;
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
                else if (playerHandStatus[i].rank == playerHandStatus[0].rank)
                {
                    // Check tie-breaker
                    if (PlayerTieLost(playerHandStatus[0], playerHandStatus[i]))
                    {
                        // Player lost go to next hand
                        ++lossCount;
                        if (calcPercentages)
                        {
                            winPercent[handNum]  = winCount  / denom;
                            tiePercent[handNum]  = tieCount  / denom;
                            lossPercent[handNum] = lossCount / denom;
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
            if (handOutcome == HandOutcome::LOST)
            {
                continue;
            }
            
            // Check tie breaker
            if (possibleTie)
            {
                for (int i = 1; i < numPlayers; ++i)
                {
                    if (playerHandStatus[i].rank == playerHandStatus[0].rank)
                    {
                        // Player must win all tie breaks to win the hand or else its a tie,
                        // because we would have caught the tie break loss above
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
                                winPercent[handNum] = winCount / denom;
                                tiePercent[handNum] = tieCount / denom;
                                lossPercent[handNum] = lossCount / denom;
                            }                            
                            break;
                        }
                    }
                }
                // If player didn't tie anyone else, they must have won
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
                        winPercent[handNum] = winCount / denom;
                        tiePercent[handNum] = tieCount / denom;
                        lossPercent[handNum] = lossCount / denom;
                    }
                }
            }
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
                    winPercent[handNum]  = winCount  / denom;
                    tiePercent[handNum]  = tieCount  / denom;
                    lossPercent[handNum] = lossCount / denom;
                }
            }
        } // end for (int handNum...

        // Write resluts to results file
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

        //// Write done to service file
        //outFile.open(outFileName, ios::out);
        //if (!outFile)
        //{
        //    cerr << "Failed to open output file \"" << outFileName << "\", exiting program\n";
        //}
        //outFile << "done\n";
        //outFile.close();

    } // end if (runSim)
    return 0;
}


// Function Definitions -------------------------------------------------------
void ReadSimInfo(ifstream &inFile, Player *playerInit, Board &boardInit, int &numRuns,
    int &numPlayers, int &calcPercentages, set<int> &pickedCardValues, int &cardsPicked)
{
    inFile >> numRuns >> numPlayers >> calcPercentages;
    for (int i = 0; i < numPlayers; ++i)
    {
        for (int j = 0; j < 2; ++j)
        {
            int c;
            inFile >> c;
            if (c != RAND_CARD_VALUE)
            {
                ++cardsPicked;
                pickedCardValues.insert(c);
                playerInit[i].cards[j].value = c % 13;
                playerInit[i].cards[j].suit = c / 13;
            }
        }
    }
    for (int i = 0; i < 5; ++i)
    {
        int c;
        inFile >> c;
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


void _swapCards(Card *c1, Card *c2)
{
    int v = c1->value, s = c1->suit;
    c1->value = c2->value;
    c1->suit = c2->suit;
    c2->value = v;
    c2->suit = s;
    return;
}


void ShuffleCards(Card *deck, int remainingCards)
{
    for (int i = remainingCards - 1; i > 0; --i)
    {
        // Pick random j such that 0<=j<=i
        int j = rand() % (i + 1);
        if (i != j)
            _swapCards(deck + i, deck + j);
    }
    return;
}


void AssignCards(Player *player, const Player *playerInit, Board &board, const Board &boardInit, const Card *deck, int numPlayers)
{
    int iDeck = 0;
    for (int i = 0; i < numPlayers; ++i)
    {
        if (playerInit[i].cards[0].value == RAND_CARD_VALUE)
        {
            player[i].cards[0].setValueSuit(deck[iDeck].value, deck[iDeck].suit);
            ++iDeck;
        }
        else
        {
            player[i].cards[0].setValueSuit(playerInit[i].cards[0].value, playerInit[i].cards[0].suit);
        }
        if (playerInit[i].cards[1].value == RAND_CARD_VALUE)
        {
            player[i].cards[1].setValueSuit(deck[iDeck].value, deck[iDeck].suit);
            ++iDeck;
        }
        else
        {
            player[i].cards[1].setValueSuit(playerInit[i].cards[1].value, playerInit[i].cards[1].suit);
        }
    }
    for (int i = 0; i < 5; ++i)
    {
        if (boardInit.cards[i].value == RAND_CARD_VALUE)
        {
            board.cards[i].setValueSuit(deck[iDeck].value, deck[iDeck].suit);
            ++iDeck;
        }
        else
        {
            board.cards[i].setValueSuit(boardInit.cards[i].value, boardInit.cards[i].suit);
        }
    }
    return;
}


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


bool _containsStraight(vector<int> &vValues, int &kicker)
{
    // Look for 5 card consecutive sequences starting with highest card
    // vector of values is sorted in descending order
    int numToCheck, i, j, startVal;

    // If ace is in vValues add it as the lowest card too
    if (vValues[0] == 12)
        vValues.push_back(-1);
    numToCheck = vValues.size() - 4;
    i = 0;
    while (i < numToCheck)
    {
        // Get starting card
        startVal = vValues[i];
        for (j = 1; j < 5; ++j)
        {
            if (vValues[i + j] != startVal - j)
                break;
            if (j == 4)
            {
                kicker = startVal;
                return true;
            }
        }
        i += j;        
    }
    return false;
}


bool _isStraight(const Card *hand, HandStatus &handStatus)
{
    vector<int> vValues;
    // Put values in a vector and sort in descending order
    for (int i = 0; i < 7; ++i)
        vValues.push_back(hand[i].value);
    sort(vValues.begin(), vValues.end(), greater<int>());
    if (_containsStraight(vValues, handStatus.kickers[0]))
    {
        handStatus.rank = HandRank::STRAIGHT;
        return true;
    }
    return false;
}


void setHandStatus(const Card *hand, HandStatus &handStatus)
{
    // Check for Royal Flush, can also check for Straight Flush & Flush
    // Put same suit cards in there own vector
    vector<int> cValues;
    vector<int> dValues;
    vector<int> hValues;
    vector<int> sValues;
    for (int i = 0; i < 7; ++i)
    {
        switch (hand[i].suit)
        {
        case 0:
            cValues.push_back(hand[i].value);
            break;
        case 1:
            dValues.push_back(hand[i].value);
            break;
        case 2:
            hValues.push_back(hand[i].value);
            break;
        case 3:
            sValues.push_back(hand[i].value);
            break;
#if DEBUG
        default:
            cerr << "Bad suit detected in _isRoyalFlush()\n";
            break;
#endif
        }
    }
    // Check lengths of each vector, if at least 5 then at least flush
    if (cValues.size() >= 5)
    {
        // Sort the values in descending order
        sort(cValues.begin(), cValues.end(), greater<int>());
        // Check for sequence of 12, 11, 10, 9, 8
        if (cValues[0] == 12 && cValues[1] == 11 && cValues[2] == 10 && cValues[2] == 9 && cValues[2] == 8)
        {
            handStatus.rank = HandRank::ROYAL_FLUSH;
            return;
        }
        else if (_containsStraight(cValues, handStatus.kickers[0]))
        {
            handStatus.rank = HandRank::STRAIGHT_FLUSH;
            return;
        }
        else
        {
            handStatus.rank = HandRank::FLUSH;
            for (int i = 0; i < 5; ++i)
                handStatus.kickers[i] = cValues[i];
        }
    }
    else if (dValues.size() >= 5)
    {
        // Sort the values in descending order
        sort(dValues.begin(), dValues.end(), greater<int>());
        // Check for sequence of 12, 11, 10, 9, 8
        if (dValues[0] == 12 && dValues[1] == 11 && dValues[2] == 10 && dValues[2] == 9 && dValues[2] == 8)
        {
            handStatus.rank = HandRank::ROYAL_FLUSH;
            return;
        }
        else if (_containsStraight(dValues, handStatus.kickers[0]))
        {
            handStatus.rank = HandRank::STRAIGHT_FLUSH;
            return;
        }
        else
        {
            handStatus.rank = HandRank::FLUSH;
            for (int i = 0; i < 5; ++i)
                handStatus.kickers[i] = dValues[i];
        }
    }
    else if (hValues.size() >= 5)
    {
        // Sort the values in descending order
        sort(hValues.begin(), hValues.end(), greater<int>());
        // Check for sequence of 12, 11, 10, 9, 8
        if (hValues[0] == 12 && hValues[1] == 11 && hValues[2] == 10 && hValues[2] == 9 && hValues[2] == 8)
        {
            handStatus.rank = HandRank::ROYAL_FLUSH;
            return;
        }
        else if (_containsStraight(hValues, handStatus.kickers[0]))
        {
            handStatus.rank = HandRank::STRAIGHT_FLUSH;
            return;
        }
        else
        {
            handStatus.rank = HandRank::FLUSH;
            for (int i = 0; i < 5; ++i)
                handStatus.kickers[i] = hValues[i];
        }
    }
    else if (sValues.size() >= 5)
    {
        // Sort the values in descending order
        sort(sValues.begin(), sValues.end(), greater<int>());
        // Check for sequence of 12, 11, 10, 9, 8
        if (sValues[0] == 12 && sValues[1] == 11 && sValues[2] == 10 && sValues[2] == 9 && sValues[2] == 8)
        {
            handStatus.rank = HandRank::ROYAL_FLUSH;
            return;
        }
        else if (_containsStraight(sValues, handStatus.kickers[0]))
        {
            handStatus.rank = HandRank::STRAIGHT_FLUSH;
            return;
        }
        else
        {
            handStatus.rank = HandRank::FLUSH;
            for (int i = 0; i < 5; ++i)
                handStatus.kickers[i] = sValues[i];
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
