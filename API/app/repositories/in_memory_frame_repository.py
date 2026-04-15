from .frame_repository import FrameRepository

class InMemoryFrameRepository(FrameRepository):
    def __init__(self):
        self.storage = {}

    def save(self, camera_id: int, frame: str):
        if camera_id not in self.storage:
            self.storage[camera_id] = []
        self.storage[camera_id].append(frame)

    def get(self, camera_id: int):
        if camera_id not in self.storage:
            return None
        return self.storage.get(camera_id).pop(0)
