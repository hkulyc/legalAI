from legal_concept_tree.concepts import get_concepts
import stanza
from stanza.server import CoreNLPClient
from common.coreNLP import *
from sentence_simplification.split_sentence import *
from common.utils import *
import gensim
from gensim.test.utils import datapath
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import pandas as pd
import nltk
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
lemma = lemmatizer.lemmatize

class Word:
    def __init__(self, id, core):
        self.value = core.value
        self.core = core
        self.id = id
        self.parent = None
        self.dep = ''
    def has_parent(self, parent, dep):
        self.parent = parent
        self.dep = dep
        
concepts = get_concepts()
keywords = set(("acl", "acl:relcl", "advcl", "obl:npmod", "advmod", "advmod:emph", "advmod:lmod", "amod", "appos", "aux", "aux:pass", "case", "cc", "cc:preconj", "ccomp", "clf", "compound", "compound:lvc", "compound:prt", "compound:redup", "compound:svc", "conj", "cop", "csubj", "csubj:pass", "dep", "det", "det:numgov", "det:nummod", "det:poss", "discourse", "dislocated", "expl", "expl:impers", "expl:pass", "expl:pv", "fixed", "flat", "flat:foreign", "flat:name", "goeswith", "iobj", "list", "mark", "nmod", "nmod:poss", "nmod:tmod", "nsubj", "nsubj:pass", "nummod", "nummod:gov", "obj", "obl", "obl:agent", "obl:arg", "obl:lmod", "obl:tmod", "orphan", "parataxis", "punct", "reparandum", "root", "vocative", "xcomp"))

def get_dep(dep, words, word, parent):
    ""
    res = None
    if dep in keywords: 
#         if abs(word.id - parent.id) == 2 and words[int((word.id + parent.id) / 2)].value == 'to':
        if word.id > 0 and words[word.id - 1].value == 'to':
            res = 'to'
        elif word.core.pos == 'VB':
            res = 'to'
        else:
            return None
    if dep.startswith('nmod:'):
        res = dep[5:]
    elif dep.startswith('obl:'):
        res = dep[4:]
    elif dep.startswith('conj:'):
        res = dep[5:]
    elif dep.startswith('advcl:'):
        res = dep[6:]
    if res != None:
        res = res.replace('_', ' ')
    return res
    
def find_place(ind, id):
    for i in range(len(ind)):
        if ind[i] >= id:
            return i
    return len(ind)

def remove_dup_words(arr):
    words = set()
    res = []
    for word in arr:
        if word not in words:
            res.append(word)
            words.add(word)
    return res

def contains(a, b):
    "if a contains b"
    if b == []:
        if a == []:
            return 0
        return 1
    id = index(a, b[0])
    if id == -1:
        return -1
    return contains(a[:id]+a[id+1:], b[1:])
    
def remove_dup(dict):
    "remove duplicate word vec from an dict of int vector pairs"
    for key in dict:
        dict[key] = remove_dup_words(dict[key])
    res = {}
    keys = list(dict.keys())
    for key in keys:
        add = True
        for i in keys:
            tmp = contains(dict[i], dict[key])
            if key != i and (tmp == 1 or (tmp == 0 and i < key)):
                add = False
                break
        if add: res[key] = dict[key]
    return res

dts = set(['DT', 'IN', 'PRP$', 'CD'])

def is_dummy(p):
    list = p.to_list()
    if len(list) == 2:
        tmp = p.children[0].value
        if tmp in dts:
            return True
    elif len(list) == 3:
        tmp = p.children[-1].value
        if tmp == 'POS':
            return True
    return False

# remove_dup({0:['to', 'the', 'future'], 1:['to', 'the', 'future']})

def combine_cluster(tags, inds, words, cons):
    
    return tags

def gen_hybrid(words, matches) -> list:
    "a hybrid method of dependency parsing and continuency parsing"
    sent = ' '.join([word.value for word in words])
    p = parse_sentence(sent).parseTree
    root = Comp(p, 0, None)
    cont = root.to_list()
    tags = {}
    inds = {}
    while len(matches) > 0:
        i = matches.pop()
        word = cont[i]
        curr = word.parent
        while curr.parent != None:
            tmp = curr.to_list()
            if curr.value.endswith('P'):
                if len(tmp) > 1:
                    break
            if len(tmp) >= 6:
                break
            curr = curr.parent
        arr = curr.to_list()
        if len(arr) <= 6:
            if is_dummy(curr):
                arr = [word]
            res = [i.value for i in arr]
            ind = [root.id(i) for i in arr]
            adv = []
            word = words[i]
    #             res.append('->'+word.value+'<-')
            while word.parent != None:
                if word.parent.id in matches:
                    matches.remove(word.parent.id)
                tags.pop(word.parent.id, None)
                # should not be punc
                if is_punc(word.parent) or word.parent.id in ind:
                    word = word.parent
                    continue
                dep = get_dep(word.dep, words, word, word.parent)
                # the condition of 系动词
                if word.parent.core.pos in ('VBP', 'VBD') and word.parent.core.lemma == 'be':
                    break
                # 主语不加动词
                if word.parent.core.pos.startswith('VB') and word.parent.id > i:
                    break
                if dep == None:
                    id = find_place(ind, word.parent.id)
                    res.insert(id, word.parent.value)
                    ind.insert(id, word.parent.id)
                else:
                    if word.id >= word.parent.id:
                        id = find_place(ind, word.parent.id)
                        res.insert(id, word.parent.value)
                        ind.insert(id, word.parent.id)
                        res.insert(id+1, dep)
                        ind.insert(id+1, word.parent.id)
    #                         print(sent)
    #                         print(word.value, word.dep, word.parent.value)
                    else:
    #                         id = find_place(ind, word.id)
                        res.insert(0, dep)
                        adv = res + adv
                        res = [word.parent.value]
                        ind = [word.parent.id]
                # stop when hit a verb
                if word.parent.core.pos.startswith('VB'):
                    break
                word = word.parent
            res.extend(adv)
            if len(res) > 1:
                tags[i] = res
                inds[i] = ind
        else:
            continue
    tags = remove_dup(tags)
    tags = combine_cluster(tags, inds, words, cont)
    for key in tags:
#         print(tags[key], inds[key], key)
        id = index(tags[key], words[key].value)
        tags[key][id] = '->'+tags[key][id]+'<-'
    return [' '.join(value) for value in tags.values()]

def gen_con(words, matches) -> list:
    "generate the tags based on continuency parsing"
    sent = ' '.join([word.value for word in words])
    p = parse_sentence(sent).parseTree
    cont = Comp(p, 0, None).to_list()
    tags = {}
    for i in matches:
        word = cont[i]
        curr = word.parent
        while curr.parent != None:
            tmp = curr.to_list()
            if curr.value.endswith('P'):
                if len(tmp) > 1:
                    break
            if len(tmp) >= 6:
                break
            curr = curr.parent
        tmp = [word.value for word in curr.to_list()]
        # length limit
        if len(tmp) <= 6 and not is_dummy(curr):
            tags[i] = tmp
    tags = remove_dup(tags)
    return [' '.join(value) for value in tags.values()]

def gen_dep(words, matches) -> list:
    "generate the tags based on dependency parsing"
    tags = {}
    count = 0
    for i in matches:
        res = []
        ind = []
        adv = []
        word = words[i]
#             res.append('->'+word.value+'<-')
        res.append(word.value)
        ind.append(word.id)
        while word.parent != None:
            dep = get_dep(word.dep, words, word, word.parent)
            # should not be punc
            if is_punc(word.parent):
                word = word.parent
                continue
            if dep == None:
                id = find_place(ind, word.parent.id)
                res.insert(id, word.parent.value)
                ind.insert(id, word.parent.id)
            else:
                if word.id >= word.parent.id:
                    id = find_place(ind, word.parent.id)
                    res.insert(id, word.parent.value)
                    ind.insert(id, word.parent.id)
                    res.insert(id+1, dep)
                    ind.insert(id+1, word.parent.id)
#                         print(sent)
#                         print(word.value, word.dep, word.parent.value)
                else:
#                         id = find_place(ind, word.id)
                    res.insert(0, dep)
                    adv = res + adv
                    res = [word.parent.value]
                    ind = [word.parent.id]
            
            word = word.parent
        res.extend(adv)
#             if adv != []:
#                 print(sent)
#                 print(' '.join(res))
#             tags.append(' '.join(res))
        tags[i] = res
#     print(tags)
    tags = remove_dup(tags)
    return [' '.join(value) for value in tags.values()]


DEP = 'dep'
CON = 'con'
HYBRID = 'hybrid'
WORD = 'word'

def sent2label(sent, mode = HYBRID):
    if sent == None: return []
#     sent = 'she suffered a fracture of the superior and inferior public rami of the right pelvis.'
    dep = parse_sentence(sent)
    length = len(dep.token)
    tokens = dep.token
    words = [None]*length
    entities = find_entity(dep)
    for i in range(length):
        word = Word(i, tokens[i])
        words[i] = word
#     for edge in dep.collapsedDependencies.edge:
    for edge in dep.enhancedDependencies.edge:
        source = words[edge.source-1]
        target = words[edge.target-1]
    #     print(source.value, edge.dep, target.value)
        if source != target and not edge.dep.startswith('acl:'):
            target.has_parent(source, edge.dep)
    matches = []
    for i in range(length):
        if concepts.get(lemma(words[i].value.lower())) and not entities.has(i):
            matches.append(i)
    if mode == DEP:
        return gen_dep(words, matches)
    elif mode == CON:
        return gen_con(words, matches)
    elif mode == HYBRID:
        return gen_hybrid(words, matches)
    elif mode == WORD:
        ret = {}
        for i in matches:
            ret[i] = [lemma(words[i].value.lower())]
        ret = remove_dup(ret)
        return [' '.join(value) for value in ret.values()]
    else:
        raise Exception()