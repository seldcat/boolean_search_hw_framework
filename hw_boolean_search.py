#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import sys
import string
import re


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


class QueryTree:
    def __init__(self, qid, query):
        self.query_id = qid
        self.query = ' '.join(query.lower().split())
        self.i = 0
        self.c = None
        self.words = re.findall(r'\w+|[()| ]', query)
        self.query_tree = []
    #     каждая хуйня будет словарем, ключ - это операция, элементы - это наши слова из запроса

    def get(self):
        if self.i < len(self.words):
            self.c = self.words[self.i]
            self.i += 1
        else:
            self.c = None

    def parse_query(self):
        self.get()
        result = self._or()
        print(result)

    def _or(self):
        operand1 = self._and()
        self.get()

        while self.c == '|':
            self.get()
            operand2 = self._and()
            return {
                'op': 'or',
                'operand1': operand1,
                'operand2': operand2
            }
        else:
            return operand1

    def _and(self):
        operand1 = self._token()
        self.get()
        result = {}
        while self.c == ' ':
            self.get()
            operand2 = self._token()
            result = {
                'op': 'and',
                'operand1': operand1,
                'operand2': operand2
            }
        else:
            if result:
                return result
            else:
                return operand1
    
    def _token(self):
        if self.c == '(':
            self.get()
            result = self._or()
            if self.c == ')':
                self.get()
                return result
        else:
            return self.c

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
    # parser = argparse.ArgumentParser(description='Homework: Boolean Search')
    # parser.add_argument('--queries_file', required=True, help='queries.numerate.txt')
    # parser.add_argument('--objects_file', required=True, help='objects.numerate.txt')
    # parser.add_argument('--docs_file', required=True, help='docs.txt')
    # parser.add_argument('--submission_file', required=True, help='output file with relevances')
    # args = parser.parse_args()

    # # Build index.
    # index = Index(args.docs_file)

    # # Process queries.
    # search_results = SearchResults()
    # with codecs.open(args.queries_file, mode='r', encoding='utf-8') as queries_fh:
    #     for line in queries_fh:
    #         fields = line.rstrip('\n').split('\t')
    #         qid = int(fields[0])
    #         query = fields[1]

    #         # Parse query.
    #         query_tree = QueryTree(qid, query)

    #         # Search and save results.
    #         search_results.add(query_tree.search(index))

    # # Generate submission file.
    # search_results.print_submission(args.objects_file, args.submission_file)

    query_tree = QueryTree(0, 'hello world fine')
    query_tree.parse_query()
    pass


if __name__ == "__main__":
    main()

