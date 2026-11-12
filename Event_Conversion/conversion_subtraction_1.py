import numpy as np


class PseudoEventCamera:
    def __init__(self, threshold = 30):
        self.threshold = threshold
        self.ref = None



    def step(self, greyscale_frame):
        brightness = np.int16(greyscale_frame)

        if self.ref is None:
            self.ref = brightness.copy()
            return np.zeros_like(greyscale_frame, bool), np.zeros_like(greyscale_frame, bool)

        change = brightness - self.ref      # Vectorization

        on = change >= self.threshold
        off = change <= -self.threshold

        fired = on | off                    # Map showing which frames changed, to update values
        self.ref[fired] = brightness[fired]

        return on, off
