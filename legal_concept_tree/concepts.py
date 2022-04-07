import re
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
lemma = lemmatizer.lemmatize

class Trie:
    def __init__(self, parent, value):
        self.parent = parent
        self.value = value
        if parent:
            self.level = parent.level + 1
        else:
            self.level = 0
            
def com_level(line):
    "measure the level of a row"
    start = 6
    if not line.startswith(' '):
        num = -1
    else:
        start = re.search(r"\w", line).start()
        #     print(start)
        num = line[:start].count('.')
    return num+2, line[start:]

def get_concepts():
    file = open('taxhier_MC.txt')
    root = Trie(None, None)
    parent = [root]
    concepts = {}
    while True:
        line = file.readline()
#         print(line)
        if not line:
            break
        line = line.rstrip('\n')
        level, word = com_level(line)
    #     print(word)
        word = lemma(word.lower())
        parent = parent[:level]
        trie = Trie(parent[-1], word)
        parent.append(trie)
        concepts[word] = trie
    return concepts