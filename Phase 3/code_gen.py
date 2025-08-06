class SemanticStack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        return None

    def get_top(self):
        if not self.is_empty():
            return self.stack[-1]
        return None

class CodeGen:
    def __init__(self):
        pass

    def declare():
        pass
