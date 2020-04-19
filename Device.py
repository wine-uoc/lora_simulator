import PositionHelper 

class Device:
    pos_x = 0
    pos_y = 0

    def __init__(self, id=None, mode=None, max_x=None, max_y=None):
        assert(id != None)
        assert(mode != None)

        self.id = id
        self.pos_x, self.pos_y = PositionHelper.PositionHelper.get_position(mode=mode, max_x=max_x, max_y=max_y)

    def print_position(self):
        print("Node {} at position: x={:.1f} y={:.1f}!".format(self.id, self.pos_x, self.pos_y))

    def get_position(self):
        return (self.pos_x, self.pos_y)
    
