from nltk.parse.corenlp import CoreNLPDependencyParser
from collections import defaultdict, OrderedDict
def triples_2_idx(node_dict, base_idx):
    edge_idx_list = [list(), list()]
    rel_set = set()
    for row in node_dict:
        address = node_dict[row]['address'] + base_idx
        deps = node_dict[row]['deps']
        if deps != defaultdict():
            for rel in deps:
                for item in deps[rel]:
                    tail=item+base_idx
                    edge_idx_list[0].append(address)
                    edge_idx_list[1].append(tail)
                rel_set.add(rel)
    return edge_idx_list, rel_set


def parse_sentence(
        text):
    eng_parser = CoreNLPDependencyParser()
    res = list(eng_parser.parse(text))
    wordlist=[]
    for i in range(1,len(res[0].nodes)):
        wordlist.append(res[0].nodes[i]["word"])
    edge_idx_list, rel_set = triples_2_idx(res[0].nodes, base_idx=0)
    return edge_idx_list,wordlist


if(__name__=="__main__"):
    text=['Although', 'it', 'was', 'CBS', "'", 's', 'answer', 'to', 'N', 'BC', "'", 's', 'popular', '"', 'A', 'Date', 'with', 'Jud', 'y', '",', 'it', 'was', 'also', 'broadcast', 'by', 'N', 'BC', 'in', '', '1', '9', '4', '8', 'as', 'a', 'summer', 'replacement', 'for', '"', 'The', 'Bob', 'Hope', '".']
    edge_idx_list,wordlist=parse_sentence(text)
    print(edge_idx_list)
    print(wordlist)
