import json
import string

TEST_TREE_1 = """Input: Bob brought the pizza to Alice .
Parse:
brought VBD ROOT @2
 +-- Bob NNP nsubj @1
 +-- pizza NN dobj @4
 |   +-- the DT det @3
 +-- to IN prep @5
 |   +-- Alice NNP pobj @6
 +-- . . punct @7"""

TEST_TREE_2 = """Input: why hello there my dear friend , what has caused you to seek me out this fine evening ?
Parse:
why WRB ROOT @1
 +-- hello PRP dep @2
 +-- there EX dep @3
 +-- friend NN nsubj @6
 |   +-- my PRP$ poss @4
 |   +-- dear JJ amod @5
 |   +-- , , punct @7
 |   +-- caused VBN rcmod @10
 |       +-- what WP nsubj @8
 |       +-- has VBZ aux @9
 |       +-- you PRP dobj @11
 |       +-- seek VB xcomp @13
 |           +-- to TO aux @12
 |           +-- me PRP dobj @14
 |           +-- out RP prt @15
 |           +-- evening NN tmod @18
 |               +-- this DT det @16
 |               +-- fine JJ amod @17
 +-- ? . punct @19
"""

TEST_TREE_3 = """Input: Bob brought the pizza to Alice and it was amazingly fantastically delightfully phenomenally good.
Parse:
brought VBD ROOT @2
 +-- Bob NNP nsubj @1
 +-- pizza NN dobj @4
 |   +-- the DT det @3
 +-- to IN prep @5
 |   +-- Alice NNP pobj @6
 |   +-- and XXX yyyy @20
 |       +-- it XXX yyyy @21
 |       +-- was XXX yyyy @22
 |   +-- amazingly XXX yyyy @23
 |       +-- fantastically XXX yyyy @24
 |       +-- delightfully XXX yyyy @25
 |       +-- phenomenally XXX yyyy @26
 |   +-- good XXX yyyy @27
 +-- . . punct @7
"""

TEST_TREE_4 = """Input: I am very impressed .
Parse:
impressed JJ ROOT @4
 +-- I PRP nsubj @1
 +-- am VBP cop @2
 +-- very RB advmod @3
 +-- . . punct @5
"""

TEST_TREE_5 = """Input: Can you agree ?
Parse:
agree VB ROOT @3
 +-- Can MD aux @1
 +-- you PRP nsubj @2
 +-- ? . punct @4
"""

SPACES_PER_DEPTH_LEVEL = 4

class ParseNode:

    def __init__(self, 
                 word, 
                 part_of_speech, 
                 sentence_role, 
                 sentence_word_order, 
                 parent, 
                 depth):
        self.word = word
        self.part_of_speech = part_of_speech
        self.sentence_role = sentence_role
        self.sentence_word_order = int(sentence_word_order)
        self.parent = parent
        self.depth = int(depth)
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        return self

    def get_edges(self):
        return self._get_edges_helper([])

    def _get_edges_helper(self, edge_list):
        for child in self.children:
            edge_list.append(tuple([self, child]))
            child._get_edges_helper(edge_list)
        return edge_list

    def print_subtree(self):
        self.print_self()
        for child in self.children:
            child.print_subtree()

    def print_self(self):
        print self.__str__()    

    def to_sentence(self):
        parse_node_list = self.to_sentence_order()
        return " ".join(map(lambda x: x.word, parse_node_list))

    def to_sentence_order(self):
        index_mapping = {}
        self._to_sentence_order_helper(index_mapping)
        parse_nodes_sentence = []
        for i in range(len(index_mapping)):
            parse_nodes_sentence.append(index_mapping[i])
        return parse_nodes_sentence

    def _to_sentence_order_helper(self, index_mapping):
        index_mapping[self.sentence_word_order] = self.copy()
        for child in self.children:
            child._to_sentence_order_helper(index_mapping)

    def to_list(self):
        output_list = []
        output_list.append(self.copy())
        for child in self.children:
            output_list += child.to_list()
        return output_list

    def copy(self):
        return ParseNode(self.word, 
                self.part_of_speech, 
                self.sentence_role, 
                self.sentence_word_order, 
                self.parent, 
                self.depth)

    def subtree_to_string(self):
        return self.__str__() +\
                '\n' +\
                ''.join([child.subtree_to_string() for child in self.children])

    def __repr__(self):
        return "(word=%s, pos=%s, role=%s, depth=%d, index=%d)"\
                % (self.word, 
                   self.part_of_speech, 
                   self.sentence_role, 
                   self.depth, 
                   self.sentence_word_order)

    def __str__(self):
        output_string = ""
        for i in range(self.depth - 1):
            for i in range(SPACES_PER_DEPTH_LEVEL):
                output_string += " "
        if self.depth > 0:
            output_string += " +-- "
        output_string += "%s %s %s -- depth=%d -- index=%d"\
                % (self.word, 
                   self.part_of_speech, 
                   self.sentence_role, 
                   self.depth, 
                   self.sentence_word_order)
        return output_string

def parse_ascii_tree(ascii_tree_input):
    """
    Takes an ASCII parse tree and outputs a tree built up of 'ParseNode's.
    Example input:
    "
    Input: Bob brought the pizza to Alice .
    Parse:
    brought VBD ROOT
     +-- Bob NNP nsubj
     +-- pizza NN dobj
     |   +-- the DT det
     +-- to IN prep
     |   +-- Alice NNP pobj
     +-- . . punct
     "
    """
    level_indicator = "+--"
    root = None
    depth = 0
    parents = {}
    for line in string.split(ascii_tree_input, "\n"):
        if string.find(line, "Input:") == 0\
                or string.find(line, "Parse:") == 0\
                or not string.strip(line):
            continue

        if root is None:
            # line of form: "<word> <part of speech> <sentence role> @<word order>"
            root = ParseNode(
                    _get_token(line, 0), 
                    _get_token(line, 1), 
                    _get_token(line, 2), 
                    int(_get_token(line, 3)[1:]) - 1, 
                    None, 
                    0)
            parents[0] = root
        elif string.find(line, level_indicator) != -1:
            # Strip the "|" character out
            line = string.replace(line, "|", " ")
            depth = _check_depth(line)
            cur_parent = parents[depth - 1]
            # line of form: " +-- <word> <part of speech> <sentence role> @<word order>"
            cur_node = ParseNode(
                    _get_token(line, 1), 
                    _get_token(line, 2), 
                    _get_token(line, 3), 
                    (int(_get_token(line, 4)[1:]) - 1),
                    cur_parent, 
                    depth)
            cur_parent.add_child(cur_node)
            parents[depth] = cur_node

    return root

def _check_depth(line):
    """
    When '|' is replaced by a space there are 4 spaces for each level, excluding 1 extra
    space at the beginning of each line.
    Get the index that '+--' starts at, subtract 1 to account for the extra space, and 
    perform integer division on the index by SPACES_PER_DEPTH_LEVEL to get the depth.
    SPACES_PER_DEPTH_LEVEL is 4 by default
    """
    level_indicator = "+--"
    index = string.find(line, level_indicator)
    index -= 1
    return 1 + (index // SPACES_PER_DEPTH_LEVEL)


def _get_token(line, token_position):
    """
    Get the token at the index specified by 'token_position' when 'line' is tokenized
    by splitting on single spaces.
    """
    return string.split(string.strip(line), " ")[token_position]

def _print_divider():
    print("\n-------------------------------------------\n")

def parsing_tests():
    print "Parsing Tests"
    print "============="

    output_tree_1 = parse_ascii_tree(TEST_TREE_1)
    print "\nOutput from parse_ascii_tree with test tree 1"
    output_tree_1.print_subtree()

    print "\n\nto_list test"
    print output_tree_1.to_list()
    _print_divider()

    output_tree_2 = parse_ascii_tree(TEST_TREE_2)
    print "\nOutput from parse_ascii_tree with test tree 2"
    output_tree_2.print_subtree()

    print "\n\nto_list test"
    print output_tree_2.to_list()
    _print_divider()

    output_tree_3 = parse_ascii_tree(TEST_TREE_3)
    print "\nOutput from parse_ascii_tree with test tree 3"
    output_tree_3.print_subtree()

    print "\n\nto_list test"
    print output_tree_3.to_list()
    _print_divider()

    output_tree_4 = parse_ascii_tree(TEST_TREE_4)
    print "\nOutput from parse_ascii_tree with test tree 4"
    output_tree_4.print_subtree()

    print "\n\nto_list test"
    print output_tree_4.to_list()
    _print_divider()

def json_tests():
    pass
    #print "JSON Tests"
    #print "=========="
    # parse_tree_to_json DNE
    #parse_tree_to_json(parse_ascii_tree(TEST_TREE_5))

def tests():
    parsing_tests()
    json_tests()

if __name__ == '__main__':
    tests()
    #print run_parsey("Test sentence input.")
