# socket_context.py
class SocketContext:
    def __init__(self):
        self._sid_to_video = {}

    def set_video(self, sid, video_id):
        self._sid_to_video[sid] = video_id

    def get_video(self, sid):
        return self._sid_to_video.get(sid)

    def remove(self, sid):
        self._sid_to_video.pop(sid, None)


socket_context = SocketContext()
