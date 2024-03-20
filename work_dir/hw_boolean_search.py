#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import re
import string
from typing import Optional

import pandas as pd
from tqdm import tqdm


class Index:
    def __init__(self, index_file):
        self.file = codecs.open(index_file, mode='r', encoding='utf-8')
        self.index_dict = dict()
        self.add_docs()
        self.file.close()

    def _add_one_doc(self, index, words):
        for word in words:
            lower_word = word.lower().translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
            if not lower_word:
                continue
            if lower_word not in self.index_dict:
                self.index_dict[lower_word] = set()
            self.index_dict[lower_word].add(index)

    def add_docs(self):
        for line in tqdm(self.file.readlines(), desc='Preparing index'):
            line = line.strip()
            index, words = line.split()[0], line.split()[1:]
            self._add_one_doc(index, words)

    def get_ids_by_word(self, word):
        return self.index_dict[word] if word in self.index_dict else set()


class Token:
    def __init__(self, operator: str, left: Optional['Token'], right: Optional['Token']):
        self.operator = operator
        self.left = left
        self.right = right


class QueryTree:
    def __init__(self, qid, query):
        self.query_id = qid
        self.query = ' '.join(query.lower().strip().split())
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

        tokens = self._clean(tokens)
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
        if current_level:
            raise ValueError

        # find the outermost and rightmost operator (AND operator has higher priority)
        min_level = 0
        min_level_operators = list(filter(lambda x: x[1] == min_level, operators))
        and_operators = list(filter(lambda x: x[1] == min_level and x[0] == ' ', operators))
        token = and_operators[-1] if and_operators else min_level_operators[-1]

        return Token(token[0], self._get_query_tree(tokens[:token[2]]), self._get_query_tree(tokens[token[2] + 1:]))

    @staticmethod
    def _clean(tokens):
        """
        delete brackets if tokens looks like (...)
        """
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
        def collapse(token):
            if isinstance(token, str):
                return index.get_ids_by_word(token)
            left = collapse(token.left)
            right = collapse(token.right)
            return left & right if token.operator == ' ' else left | right
        return self.query_id, collapse(self.query_tree)


class SearchResults:
    def __init__(self):
        self.results = []

    def add(self, found):
        qid, search_result = found
        self.results.append(search_result)

    def print_submission(self, objects_file, submission_file):
        df = pd.read_csv(objects_file)
        f = open(submission_file, 'w')
        f.write('ObjectId,Relevance\n')
        for qid in df['QueryId'].unique():
            values = zip(df[df['QueryId'] == qid]['DocumentId'].values, df[df['QueryId'] == qid]['ObjectId'].values)
            for elem in values:
                f.write(','.join([str(elem[1]), str(int(elem[0] in self.results[qid - 1]))]) + '\n')
        f.close()


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
        for line in tqdm(queries_fh, desc='Searching'):
            fields = line.rstrip('\n').split('\t')
            qid = int(fields[0])
            query = fields[1]

            # Parse query.
            query_tree = QueryTree(qid, query)

            # Search and save results.
            search_results.add(query_tree.search(index))

    # Generate submission file.
    search_results.print_submission(args.objects_file, args.submission_file)


if __name__ == "__main__":
    main()
