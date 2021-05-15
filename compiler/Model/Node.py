from typing import List
from Model.BuildMessage import BuildMessage

class Node:
    def __init__(self, token):
        self._token = token

    def check_semantics(self, warnings, errors):
       pass

    def location(self):
        if self._token:
            return self._token.line, self._token.column
        else: # We often leave the token empty in unit tests
            return 0,0

    def add_message(self, message:str, messages:List[BuildMessage]):
        line, column = self.location()
        messages.append(BuildMessage(line, column, message))