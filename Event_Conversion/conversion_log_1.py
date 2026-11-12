import numpy as np


class PseudoEventCamera:
    def __init__(self, threshold = 0.2):
        self.threshold = threshold
        self.ref = None
        self.log_lookup = np.log(np.arange(256, dtype=np.float32) + 1)


    def step(self, greyscale_frame):
        brightness = self.log_lookup[greyscale_frame]

        if self.ref is None:
            self.ref = brightness.copy()
            return np.zeros_like(greyscale_frame, bool), np.zeros_like(greyscale_frame, bool)

        change = brightness - self.ref      # Vectorization

        on = change >= self.threshold
        off = change <= -self.threshold

        fired = on | off                    # Map showing which pixels fired, to update values
        self.ref[fired] = brightness[fired]

        return on, off


