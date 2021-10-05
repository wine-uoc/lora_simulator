import numpy as np

class PropagationModel:

    @staticmethod
    def FSPL(distance):
        # Get Free-Space path loss (in dB)
        # dist (km), freq (GHz)
        if distance == 0:
            return 0
        else:
            return 20*np.log10(distance/1000.0) + 20*np.log10(868.0/1000.0) + 92.45