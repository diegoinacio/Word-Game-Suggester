import pickle
import random
import zipfile
import argparse
import itertools


parser = argparse.ArgumentParser()

parser.add_argument('-s', '--samples', default=-1, type=int)
parser.add_argument('-ml', '--minimum-length', default=3, type=int)
parser.add_argument('-mo', '--maximum-order', default=3, type=int)

args = parser.parse_args()


##############
# Read files #
##############
# Import wordlist wordlist.txt file from wordlist.zip
# Downloaded from http://www.mieliestronk.com/wordlist.html
archive = zipfile.ZipFile('data/wordlist.zip', 'r')
txtFile = archive.open('wordlist.txt')
READ = txtFile.read()
txtFile.close()
archive.close()


####################
# Data preparation #
####################
# Create WORDLIST
WORDLIST = [word.decode() for word in READ.split()]
# Filter words with length greater than or equal to 3
WORDLIST = [word for word in WORDLIST if len(word) >= args.minimum_length]
# Remove words with invalid chars
WORDLIST = [word for word in WORDLIST if word.isalpha()]
# Uppercase all letters
WORDLIST = [word.upper() for word in WORDLIST]
# Select samples
if args.samples > 0:
    WORDLIST = random.sample(WORDLIST, args.samples)


##################################
# Markov chain transition matrix #
##################################

ALPHABET = ''.join([chr(i) for i in range(ord('A'), ord('Z') + 1)])
Na = len(ALPHABET)

# Letters occurrences p(x)
MCTM = {'': {e: sum([w.count(e) for w in WORDLIST]) for e in ALPHABET}}

# Transition matrix by order p(x | x_-1, x_-2, ..., x_-n)
for order in range(1, args.maximum_order+1):
    perms = sorted(set([''.join(e) for e in itertools.permutations(ALPHABET*order, order)]))
    MCTM = {**MCTM, **{a: {b: 1/Na for b in ALPHABET} for a in perms}}
    for WORD in WORDLIST:
        if len(WORD) <= order:
            continue
        for i in range(len(WORD)-order):
            MCTM[WORD[i:i+order]][WORD[i+order]] += 1

# Normalize probability
for key in MCTM.keys():
    SUM = sum(MCTM[key].values())
    MCTM[key] = {key_: MCTM[key][key_]/SUM for key_ in MCTM[key]}


########################
# Export data objects #
########################

print(f'Total words: {len(WORDLIST)}')

# Export WORDLIST
f = open('data/WORDLIST.pickle', 'wb')
pickle.dump(WORDLIST, f)
f.close()

print(f'Total chars: {sum([len(e) for e in WORDLIST])}')

# Export MCTM
f = open('data/MCTM.pickle', 'wb')
pickle.dump(MCTM, f)
f.close()
