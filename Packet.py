import logging

logger = logging.getLogger(__name__)


class Frame:

    def __init__(self, owner=None, number=None, duration=None, modulation=None, hop_duration=None, start_time=None,
                 channel=1, f_type=1, header_repetitions=1, part_num=1, n_parts=1):
        self.owner = int(owner)
        self.number = number
        self.duration = int(duration)
        self.modulation = modulation
        self.hop_duration = hop_duration
        self.start_time = int(start_time)

        # FHSS traceability specific parameters
        self.channel = channel      # freq channel
        self.f_type = f_type        # 0: header 1: payload
        self.header_repetitions = header_repetitions  # number of times the header is repeated
        self.part_num = part_num    # part number
        self.n_parts = n_parts      # number of parts into which the frame was divided

        self.end_time = start_time + self.duration
        self.collided = 0

    def divide_frame(self, hop_list, position_hop_list):
        """
        Create new frames based on this frame.

        :param hop_list:
        :param position_hop_list:
        :return: the list of new frames, the next position in hop list
        """
        # Initial values
        frames = []
        start_time = self.start_time
        pos_hop_list = position_hop_list
        part_num = 1

        # Get number of partitions
        n_pl_parts = int(self.duration // float(self.hop_duration))  # n parts of duration hop_duration
        last_part_duration = self.duration % self.hop_duration  # rest duration
        assert n_pl_parts * self.hop_duration + last_part_duration == self.duration

        if last_part_duration:
            total_num_parts = n_pl_parts + 1 + self.header_repetitions
        else:
            total_num_parts = n_pl_parts + self.header_repetitions

        # TODO: header, 40 bits
        for header in range(self.header_repetitions):
            pass
        start_time
        pos_hop_list
        part_num = self.header_repetitions

        # Payload parts of frame
        for part in range(n_pl_parts):
            start_time = start_time + self.hop_duration * part
            pos_hop_list = pos_hop_list + part
            part_num = part_num + 1
            frame = Frame(owner=self.owner,
                          number=self.number,
                          duration=self.hop_duration,
                          modulation=self.modulation,
                          hop_duration=self.hop_duration,
                          start_time=start_time,
                          channel=hop_list[pos_hop_list],
                          f_type=1,
                          header_repetitions=self.header_repetitions,
                          part_num=part_num,
                          n_parts=total_num_parts)
            frames.append(frame)

        # Remaining payload part if exists
        if last_part_duration:
            frame = Frame(owner=self.owner,
                          number=self.number,
                          duration=last_part_duration,
                          modulation=self.modulation,
                          hop_duration=self.hop_duration,
                          start_time=start_time + last_part_duration,
                          channel=hop_list[pos_hop_list + 1],
                          f_type=1,
                          header_repetitions=self.header_repetitions,
                          part_num=part_num + 1,
                          n_parts=total_num_parts)
            frames.append(frame)

        return frames, pos_hop_list + total_num_parts
