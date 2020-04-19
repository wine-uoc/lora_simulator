import matplotlib.pyplot as plt

class DeviceHelper:

    @staticmethod
    def plot_device_position(device_list=None, map_size=None):
        assert(device_list!=None)
        assert(map_size!=None)

        x_size, y_size = map_size
        device_positions = []
        for d in device_list:
            device_positions.append(d.get_position())

        x,y = zip(*device_positions)
        plt.scatter(x, y, color='b')
        
        plt.xlim((0, x_size))
        plt.ylim((0, y_size))
        plt.grid()
        plt.show()