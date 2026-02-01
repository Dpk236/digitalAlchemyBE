# socket_context.py
class SocketContext:
    def __init__(self):
        self._contexts = {}

    def set_context(self, sid, key, value):
        if sid not in self._contexts:
            self._contexts[sid] = {}
        self._contexts[sid][key] = value

    def get_context(self, sid, key):
        return self._contexts.get(sid, {}).get(key)

    def remove(self, sid):
        self._contexts.pop(sid, None)


socket_context = SocketContext()
