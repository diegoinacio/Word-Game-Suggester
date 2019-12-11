import os
import re
import sys
import pickle
import argparse
import colorama
import itertools


# Init parser
parser = argparse.ArgumentParser()

parser.add_argument(
    '-l', '--letters', required=True, type=str,
    help='All letters to be used.'
)
parser.add_argument(
    '-p', '--pattern', default='.*', type=str,
    help='Regular expression which defines the \
        pattern of all the possibilities.'
)
parser.add_argument(
    '-f', '--filter', default='', type=str,
    help='Regular expression for not allowed patterns.'
)
parser.add_argument(
    '-bp', '--bonus-point', action='store_true',
    help='Gives bonus point to words in the WORDLIST.'
)
parser.add_argument(
    '-sr', '--skip-red', action='store_true',
    help='Hides the red printed words.'
)
parser.add_argument(
    '-sy', '--skip-yellow', action='store_true',
    help='Hides the yellow printed words.'
)

args = parser.parse_args()


# Init coloram with autoreset
colorama.init(autoreset=True)


# All entries in upper case
LETTERS = ''.join([l.upper() for l in args.letters])
PATTERN = ''.join([l.upper() for l in args.pattern])
FILTER = ''.join([l.upper() for l in args.filter])


if not LETTERS.isalpha():
    raise ValueError(
        colorama.Fore.RED +
        'Invalid input letters! Try again..'
    )

if len(LETTERS) < 3:
    raise ValueError(
        colorama.Fore.RED +
        'Number of letters must be greater than or equal to 3!'
    )


def getPermutations(letters):
    '''getPermutations(letters) -> dict

    Returns all permutations mapped by word sizes, given an iterable object.

    Parameters
    ----------
    letters : iterable
        All letter to be used in the algorithm

    Returns
    -------
    dict
        A dictionary of permutations in string format, mapped by word sizes.
    '''
    perms = dict()
    for i in range(3, len(letters) + 1):
        perms[i] = set(
            [''.join(e) for e in itertools.permutations(letters, i)]
        )
    return perms


def filterPermutations(perms, pattern='.*', filter=''):
    '''filterPermutations(perms) -> dict

    Returns all permutations given an iterable object.

    Parameters
    ----------
    perms : dict
        All possible permutations.
    pattern : str, optional
        Regular expression which defines the pattern of all the possibilities.
    filter : str, optional
        Regular expression for not allowed patterns.

    Returns
    -------
    dict
        A dictionary containing all possible words for each word size.
    '''
    # Init the compilers for regular expression
    pattern_c = re.compile(f'^{pattern}$')
    filter_c = re.compile(f'^{filter}$')
    # Init the output dictionary
    perms_f = {key: [] for key in perms.keys()}
    for key, words in perms.items():
        # Loop over all words
        for word in words:
            # Pattern match for each word
            pattern_m = bool(pattern_c.match(word))
            # Filtering match for each word
            filter_m = bool(filter_c.match(word))
            # If matches and not filtered...
            if pattern_m and not filter_m:
                # ... includes to the output object
                perms_f[key] += [word]
    # Removes all keys which are empty
    perms_f = {key: perms_f[key] for key in perms_f.keys() if perms_f[key]}
    return perms_f


def getProbabilities(perms):
    '''getProbabilities(perms) -> dict

    Returns the probability of each word, given the transition matrix "MCTM"
    and the wordlist. The algorithm is inspired by the Markov chain model
    for multiple orders. Both objects (MCTM and WORDLIST) can be findded at
    data/ directory.

    Parameters
    ----------
    perms : dict
        All permutations to be considered in the algorithm.

    Returns
    -------
    dict
        A dictionary containing all probabilities.

    Data
    ----
    WORDLIST
        A list with all words used in the definition of the transition matrix.
    MCTM
        A dictionary to be used as the transition matrix.
        Each key is a previous state (multiple orders) and has as the value
        another dictionary containing the probabilities mapped by each alphabet
        letter.
    '''
    # Import the word list
    f = open('data/WORDLIST.pickle', 'rb')
    WORDLIST = pickle.load(f)
    f.close()
    # Import the transition matrix
    f = open('data/MCTM.pickle', 'rb')
    MCTM = pickle.load(f)
    f.close()
    # Get the maximum order from the transition matrix
    mOrder = max([len(key) for key in MCTM.keys()])
    # Init the probability dict
    perms_p = {key: [0]*len(perms[key]) for key in perms.keys()}
    for key, words in perms.items():
        # Loop over all words
        for i, word in enumerate(words):
            # Probability definition
            for j, e in enumerate(word):
                # Loop over each character
                if not j:
                    # If the current charactere is the first one
                    # Get the letter occurrence probability
                    perms_p[key][i] += MCTM[''][e]
                    continue
                # Clamp the substring parameter to the maximum order
                k = mOrder if j > mOrder else j
                # Get the probabilities of all possible orders
                # of previous estates for each character.
                perms_p[key][i] += sum(
                    [MCTM[word[j-l:j]][e] for l in range(1, k+1)]
                )
            # Bonus point for words in the WORDLIST
            if args.bonus_point:
                perms_p[key][i] += 1 if word in WORDLIST else 0
    return perms_p


def sortPermutations(perms, perms_p):
    '''sortPermutations(perms, perms_p) -> dict, dict

    Sort the permutations based on the probability dict.

    Parameters
    ----------
    perms : dict
        All permutations to be sorted.
    perms_p : dict
        Probabilities of the permutation.

    Returns
    -------
    dict, dict
        Two dictionaries with values sorted by its probabilities.
    '''
    # Init the dict for sorted permutations
    perms_s = dict()
    # Init the dict for sorted probabilities
    perms_ps = dict()
    for key in perms.keys():
        # Get the indices of reversely sorted probabilities
        # Similar to np.argsort function
        sort_i = [
            x[0] for x in sorted(
                enumerate(perms_p[key]),
                key=lambda x: x[1],
                reverse=True)
        ]
        # Permutations based on sorted indices
        perms_s[key] = [perms[key][i] for i in sort_i]
        # Probalities based on sorted indices
        perms_ps[key] = [perms_p[key][i] for i in sort_i]
    return perms_s, perms_ps


def showResults(perms, perms_p):
    '''sortPermutations(perms, perms_p)

    Show words ranked by probability.

    Parameters
    ----------
    perms : dict
        All permutations to be sorted.
    perms_p : dict
        Probabilities of the permutation.
    '''
    # Print header
    print(
        colorama.Back.CYAN +
        colorama.Fore.BLACK +
        '\n#######################' +
        '\n# Word Game Suggester #' +
        '\n#######################\n'
    )
    # Print separated by word sizes
    for key in perms.keys():
        # Print word length
        print(
            colorama.Back.MAGENTA +
            colorama.Fore.WHITE +
            f'\nWords length : {key} \n'
        )
        # Divide the distribution
        mini = min(perms_p[key])
        maxi = max(perms_p[key])
        for word, prob in zip(perms[key], perms_p[key]):
            # Best probabilities (print green)
            if prob > (mini + 2*(maxi - mini)/3):
                print(colorama.Fore.GREEN + word, end=' ')
            # Median probabilities (print yellow)
            elif prob > (mini + (maxi - mini)/3):
                if args.skip_yellow:
                    continue
                print(colorama.Fore.YELLOW + word, end=' ')
            # Worst probabilities (print red)
            else:
                if args.skip_red:
                    continue
                print(colorama.Fore.RED + word, end=' ')
        print('\n')


def Main():
    # Get all permutations given the input letters
    perms = getPermutations(LETTERS)
    # Filter the permutation based on input pattern
    # and filter profile.
    perms_f = filterPermutations(perms, PATTERN, FILTER)
    # Get all probabilities from the filtered permutations
    # The probability is based on the Markov Chain model
    # and the transition matrix, stored at the data/ dir.
    perms_p = getProbabilities(perms_f)
    # Sort reversely the filtered permutations based on its probabilities.
    perms_s, perms_ps = sortPermutations(perms_f, perms_p)
    # Show the result ranked by the probabilities.
    # Green and yellow words are more probable
    # Red words are very improbable
    showResults(perms_s, perms_ps)


if __name__ == '__main__':
    Main()
