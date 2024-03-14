#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import sys
import string
import re
from typing import Optional


class Index:
    def __init__(self, index_file):
        self._file = codecs.open(index_file, mode='r', encoding='utf-8')
        self._index_dict = dict()
        self._add_docs()
        self._file.close()

    def _add_one_doc(self, index, words):
        for word in words:
            lower_word = word.lower().translate(str.maketrans('', '', string.punctuation))
            if not lower_word:
                continue
            if lower_word not in self._index_dict:
                self._index_dict[lower_word] = set()
            self._index_dict[lower_word].add(index)

    def _add_docs(self):
        for line in self._file.readlines():
            line = line.strip()
            index, words = line.split()[0], line.split()[1:]
            self._add_one_doc(index, words)

    def get_ids_by_word(self, word):
        return self._index_dict[word] if word in self._index_dict else set()


class Token:
    def __init__(self, operator: str, left: Optional['Token'], right: Optional['Token']):
        self.operator = operator
        self.left = left
        self.right = right


class QueryTree:
    def __init__(self, qid, query):
        self.query_id = qid
        self.query = ' '.join(query.lower().split())
        self.query_tree = self._get_query_tree(re.findall(r'\w+|[()| ]', self.query))

    def _get_query_tree(self, tokens):
        """
        here tokens will be collected in the form (token, level, position), where
        token is a character like ' ', '|'
        level is the level at which the token is located (for searching for the outermost operator)
        position - its position in the query (for searching for the rightmost operator)
        """
        if not tokens:
            return None
        elif len(tokens) == 1:
            return tokens[0]

        tokens = self.__clean(tokens)
        operators = list()
        current_level = 0

        for i, token in enumerate(tokens):
            match token:
                case ' ':
                    operators.append((token, current_level, i))
                case '|':
                    operators.append((token, current_level, i))
                case '(':
                    current_level += 1
                case ')':
                    current_level -= 1

        # find the outermost and rightmost operator (AND operator has higher priority)
        min_level = 0
        and_operators = list(filter(lambda x: x[1] == min_level and x[0] == ' ', operators))
        token = and_operators[-1] if and_operators else operators[-1]

        return Token(token[0], self._get_query_tree(tokens[:token[2]]), self._get_query_tree(tokens[token[2] + 1:]))

    @staticmethod
    def __clean(tokens):
        brackets = []
        current_level = 0
        for token in tokens:
            match token:
                case '(':
                    current_level += 1
                    brackets.append(current_level)
                case ')':
                    brackets.append(-current_level)
                    current_level -= 1
                case _:
                    brackets.append(0)
        if brackets[0] == 1 and brackets[-1] == -1 and brackets.count(1) == 1:
            return tokens[1:-1]
        return tokens

    def search(self, index):
        # TODO: lookup query terms in the index and implement boolean search logic
        pass


class SearchResults:
    def add(self, found):
        # TODO: add next query's results
        pass

    def print_submission(self, objects_file, submission_file):
        # TODO: generate submission file
        pass


def main():
    # Command line arguments.
    parser = argparse.ArgumentParser(description='Homework: Boolean Search')
    parser.add_argument('--queries_file', required=True, help='queries.numerate.txt')
    parser.add_argument('--objects_file', required=True, help='objects.numerate.txt')
    parser.add_argument('--docs_file', required=True, help='docs.txt')
    parser.add_argument('--submission_file', required=True, help='output file with relevances')
    args = parser.parse_args()

    # Build index.
    index = Index(args.docs_file)

    # Process queries.
    search_results = SearchResults()
    with codecs.open(args.queries_file, mode='r', encoding='utf-8') as queries_fh:
        for line in queries_fh:
            fields = line.rstrip('\n').split('\t')
            qid = int(fields[0])
            query = fields[1]

            # Parse query.
            query_tree = QueryTree(qid, query)

            # Search and save results.
            search_results.add(query_tree.search(index))

    # Generate submission file.
    search_results.print_submission(args.objects_file, args.submission_file)


def test():
    query = QueryTree(1, '(GT1|GT 1)')
    return


if __name__ == "__main__":
    test()

