##################################
#     Created by Anand Gowda     #
# http://www.github.com/aceancer #
##################################

import random
import time
import string
import logging
from collections import OrderedDict
import tkinter as tk
import tkinter.simpledialog as tksd

suits = ['S', 'H', 'D', 'C']
ranks = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']

POS_TOP = 0
POS_BOTTOM = 1

logger = logging.getLogger(__name__)


def f_list(lst, sep=','):
    return sep.join([str(x) for x in lst])


def f_lists(lst, sep=' / '):
    return f_list(map(f_list, lst), sep)


class Card(object):
    def __init__(self, rank, suit=None):
        if suit is None:
            suit = rank[1]
            rank = rank[0]
        if rank not in ranks:
            raise ValueError('Card(): Invalid rank')
        if suit not in suits:
            raise ValueError('Card(): Invalid suit')
        self.rank = rank
        self.suit = suit

    @classmethod
    def card_list(cls, *args):
        lst = []
        for c in args:
            lst.append(cls(c))
            return lst

    def __str__(self):
        return self.rank + self.suit

    def __repr__(self):
        return '%s%s' % (self.rank, self.suit)

    def __hash__(self):
        return (ord(self.rank) << 8) + ord(self.suit)

    def __eq__(self, obj):
        return self.rank == obj.rank and self.suit == obj.suit

    def __ne__(self, obj):
        return self.rank != obj.rank or self.suit != obj.suit

    def __lt__(self, obj):
        return ranks.index(self.rank) > ranks.index(obj.rank)

    def __gt__(self, obj):
        return ranks.index(self.rank) < ranks.index(obj.rank)

    def __le__(self, obj):
        return ranks.index(self.rank) >= ranks.index(obj.rank)

    def __ge__(self, obj):
        return ranks.index(self.rank) <= ranks.index(obj.rank)


class Deck(object):
    def __init__(self):
        self.popped = []
        self.discarded = []
        self.active = []
        for s in suits:
            for r in ranks:
                self.active.append(Card(r, s))

    def shuffle(self):
        #Shuffle the deck.

        random.shuffle(self.active)

    def pop(self):
        #Deal the top card from the deck.

        card = self.active.pop()
        self.popped.append(card)
        return card

    def discard(self):
        card = self.active.pop()
        self.discarded.append(card)

    def return_cards(self, cards, pos=POS_BOTTOM):
        if pos not in (POS_BOTTOM, POS_TOP):
            raise Exception('Deck.return_cards(): invalid pos parameter')

        for card in cards[:]:
            if card in self.discarded:
                self.discarded.remove(card)
            elif card in self.popped:
                self.popped.remove(card)
            else:
                raise Exception('Deck.return_cards(): card not among removed cards')

        if pos == POS_BOTTOM:
            self.active[0:0] = [card]
        else:
            self.active.append(card)

    def return_discarded(self, pos=POS_BOTTOM):
        self.return_cards(self.discarded, pos)

    def return_popped(self, pos=POS_BOTTOM):
        self.return_cards(self.popped, pos)

    def return_all(self, pos=POS_BOTTOM):
        self.return_popped()
        self.return_discarded()

    def stats(self):
        return (len(self.active), len(self.popped), len(self.discarded))

    def __str__(self):
        return '[%s]' % ' '.join((str(card) for card in self.active))

    def __repr__(self):
        return 'Card(%s)' % self.__str__()


class PokerHand(object):
    #Compute the best hand from given cards, implementing traditional
    #high" poker hand ranks.

    def __init__(self, cards, evaluate=True):
        cards.sort(reverse=True)
        self.cards = cards
        if evaluate:
            self.evaluate()

    def evaluate(self):
        #Evaluate the rank of the hand.
        
        self._eval_hand_rank()
        self._fill_kickers()

    def _by_rank(self, cards=None):  #Order cards
        if cards is None:
            cards = self.cards
        ranked = OrderedDict()
        for card in cards:
            if card.rank in ranked:
                ranked[card.rank].append(card)
            else:
                ranked[card.rank] = [card]
        return ranked

    def _by_suit(self, cards=None):
        if cards is None:
            cards = self.cards
        suited = OrderedDict()
        for card in cards:
            if card.suit in suited:
                suited[card.suit].append(card)
            else:
                suited[card.suit] = [card]
        return suited

    def _find_flushes(self, cards=None):  # flushes
        if cards is None:
            cards = self.cards
        flushes = []
        for cards in self._by_suit(cards).values():
            l = len(cards)
            if l >= 5:
                for i in range(0, l - 4):
                    flushes.append(cards[i:i + 5])
        return flushes

    def _find_straights(self, cards=None):  # starights
        if cards is None:
            cards = self.cards
        straights = []
        for i in range(0, len(cards) - 4):
            card_ranks = [c.rank for c in cards[i:i + 5]]
            j = ranks.index(card_ranks[0])
            if card_ranks == ranks[j:j + 5]:
                straights.append(cards[i:i + 5])
        return straights

    def _fill_kickers(self):  # If hands are tied find winner
        hand_count = len(self.hand_cards)
        kicker_count = 5 - hand_count
        if kicker_count > 0:
            kickers = self.cards[:]
            for card in self.hand_cards:
                kickers.remove(card)
            self.kickers = kickers[:kicker_count]
        else:
            self.kickers = []
        logger.debug("kickers: %s", f_list(self.kickers))
        logger.debug("--- -------------- ---")

    def _eval_hand_rank(self):
        logger.debug("--- Evaluating %s ---", f_list(self.cards))
        straights = self._find_straights()
        if straights: logger.debug("straights: %s", f_lists(straights))
        flushes = self._find_flushes()
        if flushes: logger.debug("flushes: %s", f_lists(flushes))
        pairs = []
        threes = []
        fours = []
        for cards in self._by_rank().values():
            l = len(cards)
            if l >= 4:
                fours.append(cards[0:4])
            elif l == 3:
                threes.append(cards)
            elif l == 2:
                pairs.append(cards)
        if pairs: logger.debug("pairs: %s", f_lists(pairs))
        if threes: logger.debug("threes: %s", f_lists(threes))
        if fours: logger.debug("fours: %s", f_lists(fours))
        # straight flush
        for cards in straights:
            if cards in flushes:
                self.hand_rank = 8
                self.hand_cards = cards
                logger.debug("* straight flush: %s", f_list(self.hand_cards))
                return
        # four of a kind
        if len(fours) > 0:
            self.hand_rank = 7
            self.hand_cards = fours[0]
            logger.debug("* four of a kind: %s", f_list(self.hand_cards))
            return
        # full house
        if len(threes) > 1:
            self.hand_rank = 6
            self.hand_cards = threes[0] + threes[1][:2]
            logger.debug("* full house: %s", f_list(self.hand_cards))
            return
        elif len(threes) == 1 and len(pairs) > 0:
            self.hand_rank = 6
            self.hand_cards = threes[0] + pairs[0]
            logger.debug("* full house: %s", f_list(self.hand_cards))
            return
        # flush
        if len(flushes) > 0:
            self.hand_rank = 5
            self.hand_cards = flushes[0]
            logger.debug("* flush: %s", f_list(self.hand_cards))
            return
        # straight
        if len(straights) > 0:
            self.hand_rank = 4
            self.hand_cards = straights[0]
            logger.debug("* straight: %s", f_list(self.hand_cards))
            return
        # three of a kind
        if len(threes) > 0:
            self.hand_rank = 3
            self.hand_cards = threes[0]
            logger.debug("* three of a kind: %s", f_list(self.hand_cards))
            return
        # two pair
        if len(pairs) > 1:
            self.hand_rank = 2
            self.hand_cards = pairs[0] + pairs[1]
            logger.debug("* two pairs: %s", f_list(self.hand_cards))
            return
        # one pair
        if len(pairs) == 1:
            self.hand_rank = 1
            self.hand_cards = pairs[0];
            logger.debug("* two of a kind: %s", f_list(self.hand_cards))
            return
        # high card
        self.hand_rank = 0
        self.hand_cards = [self.cards[0]]
        logger.debug("* high card: %s", f_list(self.hand_cards))

    def __str__(self):
        return '[%s]' % f_list(self.cards)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.__str__())

    def __cmp__(self, other):
        if self.hand_rank > other.hand_rank:
            return 1
        elif self.hand_rank < other.hand_rank:
            return -1
        else:
            # same rank
            for c1, c2 in zip(self.hand_cards, other.hand_cards):
                if c1 > c2:
                    return 1
                elif c1 < c2:
                    return -1
            else:
                # same cards, check kickers
                for c1, c2 in zip(self.kickers, other.kickers):
                    if c1 > c2:
                        return 1
                    elif c1 < c2:
                        return -1
                # really, a tie
                return 0


#cmoney = 0
#money = 0
#maxb = 0
#pot = 0


def fiveCardPoker():
    clear()
    window.title("5 Card Draw")

    global cmoney
    global money
    global maxb
    global pot
    global bet
    global bet2
    global check
    global check2
    global calc
    global response

    cmoney = 500
    money = 500
    maxb = 500
    pot = 0

    response = 0

    deck = Deck()
    deck.shuffle()
    
    def cardpicture():
        global player
        global photop
        global photop2
        global photop3
        global photop4
        global photop5

        frame = tk.Frame()
        frame.pack(side=tk.TOP)
        photo = tk.PhotoImage(file=("cards_gif/" + str(player[0]) + ".gif"))
        photo = photo.subsample(2, 2)
        photop = tk.Label(frame, image=photo)
        photop.photo = photo
        photop.pack(side=tk.LEFT)
        photo2 = tk.PhotoImage(file=("cards_gif/" + str(player[1]) + ".gif"))
        photo2 = photo2.subsample(2, 2)
        photop2 = tk.Label(frame, image=photo2)
        photop2.photo = photo2
        photop2.pack(side=tk.LEFT)
        photo3 = tk.PhotoImage(file=("cards_gif/" + str(player[2]) + ".gif"))
        photo3 = photo3.subsample(2, 2)
        photop3 = tk.Label(frame, image=photo3)
        photop3.photo = photo3
        photop3.pack(side=tk.LEFT)
        photo4 = tk.PhotoImage(file=("cards_gif/" + str(player[3]) + ".gif"))
        photo4 = photo4.subsample(2, 2)
        photop4 = tk.Label(frame, image=photo4)
        photop4.photo = photo4
        photop4.pack(side=tk.LEFT)
        photo5 = tk.PhotoImage(file=("cards_gif/" + str(player[4]) + ".gif"))
        photo5 = photo5.subsample(2, 2)
        photop5 = tk.Label(frame, image=photo5)
        photop5.photo = photo5
        photop5.pack(side=tk.LEFT)
        window.update()

    def discard():
        clear()
        text = tk.Label(text="Select Cards to Discard")
        text.pack()

        global var1
        global var2
        global var3
        global var4
        global var5

        global photop
        global photop2
        global photop3
        global photop4
        global photop5

        frame = tk.Frame()
        frame.pack(side=tk.TOP)

        var1 = tk.IntVar()
        var2 = tk.IntVar()
        var3 = tk.IntVar()
        var4 = tk.IntVar()
        var5 = tk.IntVar()
        box1 = tk.Checkbutton(frame, image=photop.photo, variable=var1)
        box2 = tk.Checkbutton(frame, image=photop2.photo, variable=var2)
        box3 = tk.Checkbutton(frame, image=photop3.photo, variable=var3)
        box4 = tk.Checkbutton(frame, image=photop4.photo, variable=var4)
        box5 = tk.Checkbutton(frame, image=photop5.photo, variable=var5)
        box1.pack(side=tk.LEFT)
        box2.pack(side=tk.LEFT)
        box3.pack(side=tk.LEFT)
        box4.pack(side=tk.LEFT)
        box5.pack(side=tk.LEFT)

        submit = tk.Button(text="Submit", width=20, command=sub)
        submit.pack()

        window.update()

    def sub():
        global money
        global cmoney
        global pot
        
        clear()
        i = 0

        if var1.get() == 1:
            player[0] = deck.pop()
            i += 1
        if var2.get() == 1:
            player[1] = deck.pop()
            i += 1
        if var3.get() == 1:
            player[2] = deck.pop()
            i += 1
        if var4.get() == 1:
            player[3] = deck.pop()
            i += 1
        if var5.get() == 1:
            player[4] = deck.pop()
            i += 1

        if i == 0:
            i = tk.Label(text=("You didn't discard any cards."))
            i.pack()
        elif i == 1:
            i = tk.Label(text=("You discarded 1 card."))
            i.pack()
        else:
            i = tk.Label(text=("You discarded " + str(i) + " cards."))
            i.pack()

        window.update()
        time.sleep(1)
        clear()
        
        betd = 0

        t_hand = tk.Label(text=("Your Hand:"))
        y_money = tk.Label(text=("Your Money: $" + str(money)))
        tc_money = tk.Label(text=("Computer\'s Money: $" + str(cmoney)))
        p_pot = tk.Label(text=("Pot: $" + str(pot)))
        checkd = tk.Button(text="Check", width=20, command=check2)
        t_hand.pack()
        cardpicture()
        y_money.pack()
        tc_money.pack()
        p_pot.pack()
        if money > 0 and cmoney > 0:
            betd = tk.Button(text="Bet", width=20, command=bet2)
            betd.pack()
        checkd.pack()
    
    def calc():
        global money
        global cmoney
        global pot
        global player
        global computer
        global response
		
        if cmoney > money:
            maxb = money
        else:
            maxb = cmoney

        response = tksd.askinteger("Bet", "How Much?\nMax Bet: " + str(maxb), minvalue=1, maxvalue=maxb)
        money -= response
        cmoney -= response
        pot += response * 2
        pot = int(pot)
        money = int(money)
        cmoney = int(cmoney)
        clear()
        doc = tk.Label(text="The computer matched your bet.")
        doc.pack()
        window.update()
        time.sleep(1)
        clear()
        t_hand = tk.Label(text="Your Hand:")
        y_money = tk.Label(text=("Your Money: $" + str(money)))
        tc_money = tk.Label(text=("Computer\'s Money: $" + str(cmoney)))
        p_pot = tk.Label(text=("Pot: $" + str(pot)))
        t_hand.pack()
        cardpicture()
        y_money.pack()
        tc_money.pack()
        p_pot.pack()
        

    def bet():
        global cmoney
        global money
        global calc
        global response
		
        calc()

        cont = tk.Button(text="Continue", width=20, command=discard)
        cont.pack()
        window.update()

    def bet2():
        global cmoney
        global money
        global calc
        global response

        calc()

        cont = tk.Button(text="Continue", width=20, command=end)
        cont.pack()
        window.update()

    def check():
        clear()
        t_hand = tk.Label(text="Your Hand:")
        t_hand.pack()
        cardpicture()
        cont = tk.Button(text="Continue", width=20, command=discard)
        cont.pack()
        window.update()

    def check2():
        clear()
        t_hand = tk.Label(text="Your Hand:")
        t_hand.pack()
        cardpicture()
        cont = tk.Button(text="Continue", width=20, command=end)
        cont.pack()
        window.update()

    def end():
        global cmoney
        global money
        global pot

        pval = PokerHand(player, True)
        cval = PokerHand(computer, True)

        clear()
        '''Choose round winner'''

        if pval > cval:
            win = tk.Label(text="You won the round!")
            win.pack()
            window.update()
            money += pot
            pot = 0
        else:
            loss = tk.Label(text="You lost the round.")
            loss.pack()
            window.update()
            cmoney += pot
            pot = 0

        time.sleep(1)
        clear()

        if cmoney == 1000:
            loss2 = tk.Label(text="YOU LOST THE GAME.")
            cont = tk.Button(text="Play Again", width=20, command=fiveCardPoker)
            p_quit = tk.Button(text='Quit', width=20, command=close)
            new = tk.Button(text='Play A Different Game', width=20, command=main)
            loss2.pack()
            cont.pack()
            p_quit.pack()
            new.pack()
            window.update()
        elif money == 1000:
            win2 = tk.Label(text="YOU WON THE GAME!")
            cont = tk.Button(text="Play Again", width=20, command=fiveCardPoker)
            p_quit = tk.Button(text='Quit', width=20, command=close)
            new = tk.Button(text='Play A Different Game', width=20, command=main)
            win2.pack()
            cont.pack()
            p_quit.pack()
            new.pack()
            window.update()
        else:
            initiate()

    '''Start Game'''

    def initiate():
        clear()

        global pot
        global money
        global cmoney
        global bet
        global check
        global player
        global computer

        player = []
        computer = []

        for i in range(5):
            card = deck.pop()
            player.append(card)

        for i in range(5):
            card = deck.pop()
            computer.append(card)

        player.sort()
        computer.sort()

        pot += 10
        money -= 5
        cmoney -= 5

        p_ante = tk.Label(text="All players have anted.")
        p_ante.pack()
        window.update()
        time.sleep(1)
        clear()
        t_hand = tk.Label(text=("Your Hand:"))
        y_money = tk.Label(text=("Your Money: $" + str(money)))
        tc_money = tk.Label(text=("Computer\'s Money: $" + str(cmoney)))
        p_pot = tk.Label(text=("Pot: $" + str(pot)))
        t_hand.pack()
        cardpicture()
        y_money.pack()
        tc_money.pack()
        p_pot.pack()
        betd = tk.Button(text="Bet", width=20, command=bet)
        betd.pack()
        checkd = tk.Button(text="Check", width=20, command=check)
        checkd.pack()
        window.update()

    initiate()


def hangman():
    alphabet = list(string.ascii_lowercase)
    words = list(open("dic.txt", "r"))
    word = ""
    while len(word) < 5 or len(word) > 10:
        word = random.choice(words).lower()
    word = word.rstrip("\n")
    w = list(word)
    answer = list("_" * (len(word)))
    guess = ""
    guess_num = 6
    guesses = []

    def clear(num):
        for i in range(num):
            print(" ")
    
    clear(50)
    print("Let's play Hangman!!", "\n")

    while guess_num >= 0:
        if guess_num == 1:
            print("  ____  ")
            print("  |  O  ")
            print("  | /|\\")
            print("  | /   ")
            print("-----   ")
        elif guess_num == 2:
            print("  ____  ")
            print("  |  O  ")
            print("  | /|\\")
            print("  |     ")
            print("-----   ")
        elif guess_num == 3:
            print("  ____  ")
            print("  |  O  ")
            print("  |  |\\")
            print("  |     ")
            print("-----   ")
        elif guess_num == 4:
            print("  ____  ")
            print("  |  O  ")
            print("  |  |  ")
            print("  |     ")
            print("-----   ")
        elif guess_num == 5:
            print("  ____  ")
            print("  |  O  ")
            print("  |     ")
            print("  |     ")
            print("-----   ")
        elif guess_num == 6:
            print("  ____  ")
            print("  |     ")
            print("  |     ")
            print("  |     ")
            print("-----   ")
        elif guess_num == 0:
            print("  ____  ")
            print("  |  O  ")
            print("  | /|\\")
            print("  | / \\")
            print("-----   ")
            print("You Lose...")
            print("The word was " + word + ".")
            break
        
        print(''.join(answer), "\n\n")
        print(word)
        # print(w)
        # print(list(guess))

        print("Incorrect Guesses:", ', '.join(guesses), "\n")
        print("Guesses Left:", guess_num, "\n")

        if answer == w or guess == word:
            print("You Win!!")
            break

        letter = False
        while letter == False:
            guess = str(input("Guess a letter or a word: "))
            if guess not in alphabet:
                if guess in guesses:
                    print("You've already guessed that.")
                elif len(guess) == 1:
                    print("That's not a letter.")
                elif len(guess) != len(word):
                        print("That's too short.")
                elif guess == word:
                    letter = True
                    answer = list(guess)
            elif guess in guesses:
                print("You have already guessed that.")
            else:
                letter = True

        if guess in w:
            for i in range(len(word)):
                if guess == w[i]:
                    if len(guess) > len(word):
                        print("That's too long.")
                    elif len(guess) == 0:
                        print("You didn't type anything.")
                    elif len(guess) < len(word):
                        answer[i] = w[i]
        else:
            guess_num -= 1
            guesses.append(guess)

        clear(50)

play = ""
window = tk.Tk()


def main():
    clear()
    window.title("Games")
    window.geometry("800x600")
    text = tk.Label(text='What game would you like to play?')
    p_poker = tk.Button(text='Poker', width=20, command=fiveCardPoker)
    p_hang = tk.Button(text='Hangman', width=20, command=hangman)
    p_quit = tk.Button(text='Quit', width=20, command=close)
    text.pack()
    p_poker.pack()
    p_hang.pack()
    p_quit.pack()
    window.mainloop()


def close():
    window.destroy()


def clear():
    for widget in window.winfo_children():
        widget.destroy()


main()