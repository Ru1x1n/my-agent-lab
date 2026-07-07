class ConversationMemory:
    """管理多轮对话的短期记忆。"""
    def __init__(self, max_turns=10):
        self.history = []
        self.max_turns = max_turns

    def add(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-self.max_turns * 2:]

    def get(self):
        return self.history

    def clear(self):
        self.history = []