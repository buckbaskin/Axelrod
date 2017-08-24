"""
Additional strategies from Axelrod's second tournament.
"""

import random

from axelrod.action import Action
from axelrod.player import Player
from axelrod.random_ import random_choice

C, D = Action.C, Action.D


class Champion(Player):
    """
    Strategy submitted to Axelrod's second tournament by Danny Champion.

    This player cooperates on the first 10 moves and plays Tit for Tat for the
    next 15 more moves. After 25 moves, the program cooperates unless all the
    following are true: the other player defected on the previous move, the
    other player cooperated less than 60% and the random number between 0 and 1
    is greater that the other player's cooperation rate.

    Names:

    - Champion: [Axelrod1980b]_
    """

    name = "Champion"
    classifier = {
        'memory_depth': float('inf'),
        'stochastic': True,
        'makes_use_of': set(["length"]),
        'long_run_time': False,
        'inspects_source': False,
        'manipulates_source': False,
        'manipulates_state': False
    }

    def strategy(self, opponent: Player) -> Action:
        current_round = len(self.history)
        expected_length = self.match_attributes['length']
        # Cooperate for the first 1/20-th of the game
        if current_round == 0:
            return C
        if current_round < expected_length / 20:
            return C
        # Mirror partner for the next phase
        if current_round < expected_length * 5 / 40:
            return opponent.history[-1]
        # Now cooperate unless all of the necessary conditions are true
        defection_prop = opponent.defections / len(opponent.history)
        if opponent.history[-1] == D:
            r = random.random()
            if defection_prop >= max(0.4, r):
                return D
        return C


class Eatherley(Player):
    """
    Strategy submitted to Axelrod's second tournament by Graham Eatherley.

    A player that keeps track of how many times in the game the other player
    defected. After the other player defects, it defects with a probability
    equal to the ratio of the other's total defections to the total moves to
    that point.

    Names:

    - Eatherley: [Axelrod1980b]_
    """

    name = "Eatherley"
    classifier = {
        'memory_depth': float('inf'),
        'stochastic': True,
        'makes_use_of': set(),
        'long_run_time': False,
        'inspects_source': False,
        'manipulates_source': False,
        'manipulates_state': False
    }

    @staticmethod
    def strategy(opponent: Player) -> Action:
        # Cooperate on the first move
        if not len(opponent.history):
            return C
        # Reciprocate cooperation
        if opponent.history[-1] == C:
            return C
        # Respond to defections with probability equal to opponent's total
        # proportion of defections
        defection_prop = opponent.defections / len(opponent.history)
        return random_choice(1 - defection_prop)


class Tester(Player):
    """
    Submitted to Axelrod's second tournament by David Gladstein.

    This strategy is a TFT variant that attempts to exploit certain strategies. It
    defects on the first move. If the opponent ever defects, TESTER 'apologies' by
    cooperating and then plays TFT for the rest of the game. Otherwise TESTER
    alternates cooperation and defection.

    This strategy came 46th in Axelrod's second tournament.

    Names:

    - Tester: [Axelrod1980b]_
    """

    name = "Tester"
    classifier = {
        'memory_depth': float('inf'),
        'stochastic': False,
        'makes_use_of': set(),
        'long_run_time': False,
        'inspects_source': False,
        'manipulates_source': False,
        'manipulates_state': False
    }

    def __init__(self) -> None:
        super().__init__()
        self.is_TFT = False

    def strategy(self, opponent: Player) -> Action:
        # Defect on the first move
        if not opponent.history:
            return D
        # Am I TFT?
        if self.is_TFT:
            return D if opponent.history[-1:] == [D] else C
        else:
            # Did opponent defect?
            if opponent.history[-1] == D:
                self.is_TFT = True
                return C
            if len(self.history) in [1, 2]:
                return C
            # Alternate C and D
            return self.history[-1].flip()


class Gladstein(Player):
    """
    Submitted to Axelrod's second tournament by David Gladstein.

    This strategy is also known as Tester and is based on the reverse
    engineering of the Fortran strategies from Axelrod's second tournament.

    This strategy is a TFT variant that defects on the first round in order to
    test the opponent's response. If the opponent ever defects, the strategy
    'apologizes' by cooperating and then plays TFT for the rest of the game.
    Otherwise, it defects as much as possible subject to the constraint that
    the ratio of its defections to moves remains under 0.5, not counting the
    first defection.

    Names:

    - Gladstein: [Axelrod1980b]_
    - Tester: [Axelrod1980b]_
    """

    name = "Gladstein"
    classifier = {
        'memory_depth': float('inf'),
        'stochastic': False,
        'makes_use_of': set(),
        'long_run_time': False,
        'inspects_source': False,
        'manipulates_source': False,
        'manipulates_state': False
    }

    def __init__(self) -> None:
        super().__init__()
        # This strategy assumes the opponent is a patsy
        self.patsy = True

    def strategy(self, opponent: Player) -> Action:
        # Defect on the first move
        if not self.history:
            return D
        # Is the opponent a patsy?
        if self.patsy:
            # If the opponent defects, apologize and play TFT.
            if opponent.history[-1] == D:
                self.patsy = False
                return C
            # Cooperate as long as the cooperation ratio is below 0.5
            cooperation_ratio = self.cooperations / len(self.history)
            if cooperation_ratio > 0.5:
                return D
            return C
        else:
            # Play TFT
            return opponent.history[-1]


class MoreGrofman(Player):
    """
    Submitted to Axelrod's second tournament by Bernard Grofman.

    This strategy has 3 phases:
    1. First it cooperates on the first two rounds
    2. For rounds 3-7 inclusive, it plays the same as the opponent's last move
    3. Thereafter, it applies the following logic

      - If its own previous move was C and the opponent has defected less than
        twice in the last 7 rounds, cooperate
      - If its own previous move was C and the opponent has defected twice or
        more in the last 7 rounds, defect
      - If its own previous move was D and the opponent has defected only once
        or not at all in the last 7 rounds, cooperate
      - If its own previous move was D and the opponent has defected more than
        once in the last 7 rounds, defect

    Names:
    - Grofman's strategy: [Axelrod1980b]_
    """
    name = "MoreGrofman"
    classifier = {
        'memory_depth': 7,
        'stochastic': False,
        'makes_use_of': set(),
        'long_run_time': False,
        'inspects_source': False,
        'manipulates_source': False,
        'manipulates_state': False
    }

    def __init__(self) -> None:
        super().__init__()

    def strategy(self, opponent: Player) -> Action:
        if len(opponent.history) >= 1:
            jpick = opponent.history[-1]
        else:
            jpick = C
        moven = len(self.history) + 1 # index from 1 for fortran logic
        ioppnt = opponent.history
        return self.k86r(jpick, moven, ioppnt)

    def k86r(self, jpick, moven, ioppnt):
        """
        Originally by Bernard Grofman
        From cards by "JM" 3/27/79

        jpick = what the opponent picked last turn
        moven = move number (+1 because fortran was indexed from 1)
        iscore, jscore, random are not referenced in the Fortran function
        ja appears to be the last value picked?
        """
        # DIMENSION IOPPNT(999) # declare an array of size 999
        # k86r = ja # choosing to skip this line
        if not moven > 2:
            return C
        elif not moven > 7:
            return jpick
        else:
            myold = self.history[-1] # originally MYOLD = K86R
            iprev7 = 0
            j = moven - 7
            k = moven - 1
            #       DO 25 I = J,K
            # 25        IPREV7 = IPREV7 + IOPPNT(I)
            # Do loop where I iterates from J to K with the default step of 1
            # The 25 specifies label (25) that ends the loop
            # IOPPNT includes the opponent's last moves (0 = C, 1 = D)
            for i in range(j-1, k+1): # index range j to k inclusive
                python_index = i - 1
                iprev7 = iprev7 + int(ioppnt[python_index] == D)

            if myold == C and iprev7 <= 2:
                return C
            if myold == C and iprev7 > 2:
                return D
            if myold == D and iprev7 <= 1:
                return C
            if myold == D and iprev7 > 1:
                return D

