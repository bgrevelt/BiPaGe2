class Node:
    def __init__(self, token):
        self._token = token

    def check_semantics(self, warnings, errors):
       pass

    def location(self):
        return self._token.line, self._token.column