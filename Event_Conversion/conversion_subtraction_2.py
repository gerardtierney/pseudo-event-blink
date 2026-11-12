import numpy as np


class PseudoEventCamera:
    def __init__(self, threshold = 30):
        self.threshold = threshold
        self.ref = None



    def step(self, greyscale_frame):

        if self.ref is None:
            self.ref = greyscale_frame.copy()
            return np.zeros_like(greyscale_frame, bool), np.zeros_like(greyscale_frame, bool)

        threshold_on =  self.ref + self.threshold       # Vectorization
        threshold_off = self.ref - self.threshold

        on = (threshold_on >= self.ref) & (threshold_on < greyscale_frame)
        off = (threshold_off <= self.ref) & (threshold_off > greyscale_frame)

        fired = on | off                    # Map showing which pixels fired, to update values
        self.ref[fired] = greyscale_frame[fired]

        return on, off
