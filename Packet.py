import logging

logger = logging.getLogger(__name__)


class Frame:

    def __init__(self, owner=None, number=None, duration=None, modulation=None, start_time=None):
        self.owner = int(owner)
        self.number = int(number)
        self.duration = int(duration)
        self.modulation = modulation
        self.start_time = int(start_time)

        self.end_time = start_time + self.duration
        self.collided = 0

        # divide packet into frames of length period hop
        def generate_frames():
            pass


