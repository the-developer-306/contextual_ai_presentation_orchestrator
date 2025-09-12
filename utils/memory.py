from langchain.memory import ConversationBufferMemory
import json
import os

MEMORY_FILE = "memory/session_memory.json"

class MemoryManager:
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="history", return_messages=True)
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        self._load()

    def _load(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    data = json.load(f)
                    for msg in data.get("history", []):
                        self.memory.chat_memory.add_user_message(msg["user"])
                        self.memory.chat_memory.add_ai_message(msg["ai"])
            except Exception:
                pass

    def save(self):
        history = []
        for msg in self.memory.chat_memory.messages:
            if msg.type == "human":
                history.append({"user": msg.content, "ai": None})
            elif msg.type == "ai":
                if history and history[-1]["ai"] is None:
                    history[-1]["ai"] = msg.content
        with open(MEMORY_FILE, "w") as f:
            json.dump({"history": history}, f, indent=2)

    def add_turn(self, user, ai):
        self.memory.chat_memory.add_user_message(user)
        self.memory.chat_memory.add_ai_message(ai)
        self.save()

    def get_context(self):
        return self.memory.load_memory_variables({})["history"]
