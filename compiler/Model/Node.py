from typing import List
from compiler.Model.BuildMessage import BuildMessageContainer

class Node:
    def __init__(self, token):
        self._token = token

    def location(self):
        if self._token:
            return self._token.line, self._token.column
        else: # We often leave the token empty in unit tests
            return 0,0

    def add_error(self, message:str, messages:BuildMessageContainer):
        line, column = self.location()
        messages.add_error(message, line, column)

    def add_warning(self, message:str, messages:BuildMessageContainer):
        line, column = self.location()
        messages.add_warning(message, line, column)