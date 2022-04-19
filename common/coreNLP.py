from stanza.server import CoreNLPClient
import stanza
import logging, sys
logging.disable(sys.maxsize)
import pathlib

# Before importing this module, make sure that coreNLP server is running:

def parse_sentence(sent):
    with CoreNLPClient(endpoint='http://localhost:9010',
                       annotators=['tokenize','ssplit','pos','lemma','ner', 'parse', 'depparse','coref'],
                       start_server=stanza.server.StartServer.TRY_START,
                       properties = str(pathlib.Path(__file__).parent.resolve())+'/corenlp_server-22d5b7f37b8f4735.props') as client:
        sent = client.annotate(sent).sentence[0]
        return sent
    
class Entity:
        def __init__(self, start, end):
            self.start = start
            self.end = end
            
class Entities:
    def __init__(self):
        self.value = []
    
    def add(self, entity):
        for i in self.value:
            if entity.start >= i.start and entity.end <= i.end:
                return False
        self.value.append(entity)
        return True
    
    def has(self, index):
        for e in self.value:
            if index >= e.start and index <= e.end:
                return True
        return False
    
def starts_cap(word):
    if word == None or len(word) == 0:
        return False
    return word[0].isupper()

def find_entity(nlp):
    # find capital words
    ret = Entities()
    last_cap = []
    for i in range(len(nlp.token)):
        token = nlp.token[i]
        if starts_cap(token.word):
            if last_cap == [] or i - last_cap[-1] <= 2:
                last_cap.append(i)
            else:
                if len(last_cap) >= 2:
                    e = Entity(last_cap[0],last_cap[-1])
                    ret.add(e)
                last_cap = [i]
        if i == len(nlp.token) - 1 and len(last_cap) >= 2:
            e = Entity(last_cap[0],last_cap[-1])
            ret.add(e)
#         print(last_cap)
    mentions = nlp.mentions
    for mention in mentions:
        # only add entities more than one word
        if mention.tokenEndInSentenceExclusive - mention.tokenStartInSentenceInclusive > 1:
            e = Entity(mention.tokenStartInSentenceInclusive, mention.tokenEndInSentenceExclusive - 1)
            ret.add(e)
    return ret