import pickle
import zipfile
import itertools


##############
# Read files #
##############
# Import wordlist wordlist.txt file from wordlist.zip
# Downloaded from https://github.com/dwyl/english-words
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
WORDLIST = [word for word in WORDLIST if len(word) >= 3]
# Remove words with invalid chars
WORDLIST = [word for word in WORDLIST if word.isalpha()]
# Uppercase all letters
WORDLIST = [word.upper() for word in WORDLIST]


##################################
# Markov chain transition matrix #
##################################

ALPHABET = ''.join([chr(i) for i in range(ord('A'), ord('Z') + 1)])
Na = len(ALPHABET)

# First order transition matrix definition
MCTM = {a: {b: 1/Na for b in ALPHABET} for a in ALPHABET}
for WORD in WORDLIST:
    for a, b in zip(WORD[:-1], WORD[1:]):
        MCTM[a][b] += 1

# Second order transition matrix definition
perms = sorted(set([''.join(e) for e in itertools.permutations(ALPHABET*2, 2)]))
MCTM = {**MCTM, **{a: {b: 1/Na for b in ALPHABET} for a in perms}}
for WORD in WORDLIST:
    for i in range(len(WORD)-2):
        MCTM[WORD[i:i+2]][WORD[i+2]] += 1

# Normalize probabilities
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
