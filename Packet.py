import logging

logger = logging.getLogger(__name__)


class Frame:

    def __init__(self, owner=None, number=None, duration=None, modulation=None, hop_duration=None, start_time=None):
        self.owner = int(owner)
        self.number = number
        self.duration = int(duration)
        self.modulation = modulation
        self.hop_duration = hop_duration
        self.start_time = int(start_time)

        self.end_time = start_time + self.duration
        self.collided = 0

        # FHSS traceability specific parameters
        self.channel = 1    # freq channel
        self.type = 0       # 0: header 1: payload
        self.header_repetitions = 0     # number of times the header is repeated
        self.part = 1       # part number
        self.n_parts = 0    # number of parts into which the frame was divided

    def divide_frame(self):
        """
        Create new frames from this frame.
        :return: the list of new frames
        """
        # Get number of partitions
        n_parts = int(self.duration // float(self.hop_duration))  # n parts of duration hop_duration
        last_part_duration = self.duration % self.hop_duration    # rest duration
        assert n_parts * self.hop_duration + last_part_duration == self.duration

        # TODO: divide the frame





