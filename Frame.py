import logging

logger = logging.getLogger(__name__)


class Frame:

    def __init__(self, owner=None, number=None, duration=None, start_time=None,hop_duration=0, 
            channel=-1, is_header=0, num_header=1, part_num=0, n_parts=1):
        """Initializes a Frame instance

        Args:
            owner (int, optional): ID of the device which generated this frame. Defaults to None.
            number (int, optional): frame number for the device which generated this frame. Defaults to None.
            duration (int, optional): duration of the frame (ms). Defaults to None.
            start_time (int, optional): start time. Defaults to None.
            hop_duration (int, optional): hop duration. Defaults to 0.
            channel (int, optional): channel which the frame is transmitted in. Defaults to -1.
            is_header (int, optional): 1-> frame is a packet header, 0-> frame is a packet payload. Defaults to 0.
            num_header (int, optional): number of times the header is repeated. Defaults to 1.
            part_num (int, optional): part number of this frame. Defaults to 0.
            n_parts (int, optional): number of parts which the frame was divided into. Defaults to 1.
        """
        
        self.owner        = int(owner)
        self.number       = number
        self.duration     = int(duration)   # must fit simulation array resolution
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
        """Create sub frames based on self frame

        Args:
            hop_list ([int]): list of frequencies
            position_hop_list (int): position index for the hop_list
            hop_duration (int): hop duration
            header_duration (int): header duration (ms)
            num_rep_header (int): number of times the header is repeated

        Returns:
            ([Frame], int): 2-tuple (list of subframes, next position in hop list)
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

    def get_owner(self):
        """Gets owner of the frame

        Returns:
            int: device id from the owner of the frame
        """
        return self.owner
    
    def get_duration(self):
        """Frame duration

        Returns:
            int: frame duration (ms)
        """         
        return self.duration

    def get_number(self):
        """Frame number of the device which generated this frame.

        Returns:
            int: frame number
        """
        return self.number

    def get_part_num(self):
        """Part number of this frame

        Returns:
            int: part number
        """
        return self.part_num

    def get_num_parts(self):
        """NUmber of parts which the frame was divided into

        Returns:
            int: number of parts
        """
        return self.n_parts

    def get_start_time(self):
        """Start time of the frame

        Returns:
            int: start time
        """
        return self.start_time

    def get_end_time(self):
        """End time of the frame

        Returns:
            int: end time
        """
        return self.end_time

    def get_num_header_rep(self):
        """Gets number of times the header is repeated

        Returns:
            int: number of header repetitions
        """
        return self.num_header

    def get_is_header(self):
        """Gets if the frame is a header

        Returns:
            bool: True -> frame is a header, False -> otherwise
        """
        return self.is_header

    def get_channel(self):
        """Gets the channel where the frame is transmitted in

        Returns:
            int: channel
        """
        return self.channel

    def get_is_collided(self):
        """Gets if the frame has collided

        Returns:
            bool: True -> frame has collided, False -> otherwise
        """
        return self.collided
    
    def set_collided(self, value):
        """Set collision

        Args:
            value (bool): True-> frame has collided, False-> otherwise
        """
        self.collided = value

    def serialize(self):
        """Serializes the attributes of the Frame instance which allow allocating this Frame into
        the simulation grid.

        Returns:
            (int, int, int, int, int, int): 6-tuple (frame_channel, start_time, end_time, owner, number, part_num)
        """
        return (self.channel, self.start_time, self.end_time,
                self.owner, self.number, self.part_num)