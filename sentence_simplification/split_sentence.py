from common.coreNLP import *
from common.utils import *

class find_key:
        
    def add(self, key, value):
        if self.value.get(key) != None:
            if self.value.get(key) == []:
                self.value.get(key).append(value)
            elif self.value.get(key)[0].level > value.level:
                self.value[key] = [value]
            elif self.value.get(key)[0].level == value.level:
                self.value.get(key).append(value)
                
    def get(self, key):
        return self.value.get(key)
    
    def proc(self, p):
        if p.value == 'CC':
            self.add('CC', p)
            for child in p.parent.children:
                if child.value == ',':
                    self.add('CC', child)
        elif p.value == 'SBAR' and p.children != [] and p.children[0].value in ['IN', 'WHADVP'] and 'S' in [child.value for child in p.children]:
            self.add('SBAR', p)
            
    def dfs(self, p):
        self.proc(p)
        for child in p.children:
            self.dfs(child)
            
    def __init__(self, p):
        self.value = {'CC': [], 'SBAR': []}
        self.dfs(p)
        
    def remove_entity(self, e):
        for key in self.value:
            new = []
            for i in self.value[key]:
                id = i.root().id(i)
                if not e.has(id):
                    new.append(i)
            self.value[key] = new
            
class Comp:
    def __init__(self, parseTree, level, parent):
        self.children = []
        self.parent = parent
        self.level = level
        if parseTree != None:
            self.value = parseTree.value # can be either a word or keyword
            for child in parseTree.child:
                self.children.append(Comp(child, level + 1, self))
        else:
            self.value = None
            
    def copy_helper(self, p, level, parent):
        new = Comp(None, 0, None)
        new.value = p.value # can be either a word or keyword
        new.children = []
        new.parent = parent
        new.level = level
        for child in p.children:
            new.children.append(self.copy_helper(child, level + 1, new))
        if p == self.ccp:
            self.ret = new
        return new
            
    def copy(self, ccp):
        self.ret = None
        self.ccp = ccp
        root = self.copy_helper(self, 0, None)
        return self.ret, root
    
    def to_string_helper(self):
        ret = []
        for child in self.children:
            if child.children == []:
                ret.append(child.value)
            else:
                ret.extend(child.to_string_helper())
        return ret
    def to_string(self):
        return " ".join(self.to_string_helper())
    
    def root(self):
        while self.parent != None:
            self = self.parent
        return self
    
    def id(self, p):
        "the id of p in the tree"
        count = 0
        queue = [self]
        while(len(queue) > 0):
            curr = queue.pop()
#             print(curr.value)
            if curr == p:
                return count
            elif curr.children == []:
                count += 1
            for child in curr.children[::-1]:
                queue.append(child)
        return -1
    
    def to_list(self):
        ret = []
        queue = [self]
        while(len(queue) > 0):
            curr = queue.pop()
            if curr.children == []:
                ret.append(curr)
            else:
                for child in curr.children[::-1]:
                    queue.append(child)
        return ret
        
def s_compound(comps):
#     comps = Comp(p, 0, None)
    cache = find_key(comps)
    cc = cache.get('CC')
    if cc == []:
        return [p]
    else:
        res = []
        for cc_sib in cc[0].parent.children:
            if cc_sib not in cc:
                new, root = comps.copy(cc_sib)
                index = cc_sib.parent.parent.children.index(cc_sib.parent)
                cc_sib.parent = new.parent.parent
                new.parent.parent.children[index] = new
                res.append(root)
    return res

def is_punc(p):
    puncs = set([',', '.', '!', '?', ';', ':'])
    if p.value in puncs:
        return True
    return False

def refine_comp(comp):
    return comp
    

def s_complex(comps):
#     comps = Comp(p, 0, None)
    cache = find_key(comps)
    sbar = cache.get('SBAR')
    if sbar == []:
        return [comps], {'complex': True, 'compound': True}
    else:
        res = []
        # sbar should have lenght 1?
        sbar = sbar[0]
        s = None
        for child in sbar.children:
            if child.value == 'S':
                s = child
        tmp = [child.value for child in s.children]
        # if s begins with NP
        if index(tmp, 'NP') >= 0 and index(tmp, 'NP') < index(tmp, 'VP'):
            root = Comp(None, 0, None)
            root.children.append(s)
            s.parent = root
            res.append(root)
#             root2 = Comp(None, 0, None)
#             s2 = Comp(None, 0, root)
#             root2.children.append(s2)
            children = [child for child in sbar.parent.children if child != sbar and not is_punc(child)]
            if children == [] and sbar.parent.parent != None:
                sbar.parent.parent.children.remove(sbar.parent)
            sbar.parent.children = children
            res.append(comps)
        # if s does not start with NP
        elif index(tmp, 'VP') >= 0:
            root = Comp(None, 0, None)
            root.children.append(s)
            s.parent = root
            res.append(root)
#             root2 = Comp(None, 0, None)
#             s2 = Comp(None, 0, root)
#             root2.children.append(s2)
            children = [child for child in sbar.parent.children if child != sbar and not is_punc(child)]
            if children == [] and sbar.parent.parent != None:
                sbar.parent.parent.children.remove(sbar.parent)
            sbar.parent.children = children
            comps = refine_comp(comps)
            res.append(comps)
            vbz = None
            if len(children) > 1:
                vbz = children[1].children[0]
            else:
                return [comps], {'complex': False, 'compound': True}
            if vbz.value in ['VBD', 'VBZ']:
                s.children.insert(0, vbz)
            np = children[0]
            if np.value == 'NP':
                s.children.insert(0, np)
        else: return [comps], {'complex': False, 'compound': True}     # there must be something wrong with the coreNLP
        return res, {'complex': True, 'compound': True}
    
def split_sentence_helper(comp, if_complex, if_compound):
#     print(comp.to_string())
    cache = find_key(comp)
    p = parse_sentence(comp.to_string())
    entities = find_entity(p)
    cache.remove_entity(entities) # if the CC is in the NER, we should ignore it
    ret = []
    if cache.get('SBAR') != [] and if_complex:
        comps, cond = s_complex(comp)
        for i in comps:
            ret.extend(split_sentence_helper(i, (if_complex and cond['complex']), (if_compound and cond['compound'])))
    elif cache.get('CC') != [] and if_compound:
        comps = s_compound(comp)
        for i in comps:
            ret.extend(split_sentence_helper(i, if_complex, if_compound))
    else:
        ret = [comp]
    return ret

def split_sentence(s, complex = True, compound = True):
    p = parse_sentence(s).parseTree
    # remove the last punc
    comps = Comp(p, 0, None)
    s = comps.children[0]
    if is_punc(s.children[-1]):
        s.children.pop()
    return [i.to_string() for i in split_sentence_helper(comps, complex, compound)]