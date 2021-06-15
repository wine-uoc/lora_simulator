import logging

logger = logging.getLogger(__name__)


class Frame:

    def __init__(self, owner=None, number=None, duration=None, modulation=None, start_time=None,
                 hop_duration=0, channel=-1, is_header=0, num_header=1, part_num=0, n_parts=1):
        self.owner        = int(owner)
        self.number       = number
        self.duration     = int(duration)   # must fit simulation array resolution
        self.modulation   = modulation
        self.hop_duration = hop_duration
        self.start_time   = int(start_time)

        # FHSS traceability specific parameters
        self.channel    = channel       # freq sub channel frame is txed (-1: use all bandwidth)
        self.is_header  = is_header     # 1: header 0: payload
        self.num_header = num_header    # number of times the header is repeated
        self.part_num   = part_num      # part number
        self.n_parts    = n_parts       # number of parts into which the frame was divided

        self.end_time = start_time + self.duration
        self.collided = False

    def divide_frame(self, hop_list, position_hop_list, hop_duration, header_duration, num_rep_header):
        """
        Create temp frames based on this frame.

        :param num_rep_header:
        :param header_duration:
        :param hop_duration:
        :param hop_list:
        :param position_hop_list:
        :return: the list of temp frames, the next position in hop list
        """
        # Initial values
        frames          = []
        part_num        = self.part_num
        start_time      = self.start_time
        self.num_header = num_rep_header
        header_duration = int(header_duration)
        hop_duration    = int(hop_duration)

        # Get number of partitions
        pl_duration        = self.duration - header_duration
        n_pl_parts         = int(pl_duration // float(hop_duration))    # n parts of duration hop_duration
        last_part_duration = pl_duration % hop_duration         # rest duration
        
        # Ensure that duration matches
        assert (n_pl_parts * hop_duration + last_part_duration + header_duration == self.duration)

        # Calculate the total number of parts
        if (last_part_duration == 1):
            total_num_parts = n_pl_parts + 1 + self.num_header
        else:
            total_num_parts = n_pl_parts + self.num_header

        # Create frame header(s)
        for header in range(self.num_header):
            frame = Frame(owner=self.owner,
                          number=self.number,
                          duration=header_duration,
                          modulation=self.modulation,
                          hop_duration=header_duration,     # Header is fully transmitted in same channel
                          start_time=start_time,
                          channel=hop_list[position_hop_list],
                          is_header=1,
                          num_header=self.num_header,
                          part_num=part_num,
                          n_parts=total_num_parts)
            frames.append(frame)
            start_time = start_time + header_duration
            position_hop_list = position_hop_list + 1
            part_num = part_num + 1

        # Create payload parts
        for part in range(n_pl_parts):
            frame = Frame(owner=self.owner,
                          number=self.number,
                          duration=hop_duration,
                          modulation=self.modulation,
                          hop_duration=hop_duration,
                          start_time=start_time,
                          channel=hop_list[position_hop_list],
                          is_header=0,
                          num_header=self.num_header,
                          part_num=part_num,
                          n_parts=total_num_parts)
            frames.append(frame)
            start_time = start_time + hop_duration
            position_hop_list = position_hop_list + 1
            part_num = part_num + 1

        # Create remaining payload part if exists
        if last_part_duration:
            frame = Frame(owner=self.owner,
                          number=self.number,
                          duration=last_part_duration,
                          modulation=self.modulation,
                          hop_duration=hop_duration,
                          start_time=start_time + last_part_duration,
                          channel=hop_list[position_hop_list],
                          is_header=0,
                          num_header=self.num_header,
                          part_num=part_num,
                          n_parts=total_num_parts)
            frames.append(frame)
            position_hop_list = position_hop_list + 1

        return (frames, position_hop_list)
