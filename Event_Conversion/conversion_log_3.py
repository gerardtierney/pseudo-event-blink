import numpy as np


def create_lookups(threshold):
    values = np.arange(256)
    reference_val = values.reshape(256, 1)
    current_val = values.reshape(1, 256)
    change_per_pair = (np.log(current_val + 1) - np.log(reference_val + 1))
    on_lookup = change_per_pair >= threshold
    off_lookup = change_per_pair <= -threshold
    return on_lookup, off_lookup


class PseudoEventCamera:
    def __init__(self, threshold = 0.2):
        self.threshold = threshold
        self.ref = None
        self.on_lookup, self.off_lookup = create_lookups(threshold)


    def step(self, greyscale_frame):

        if self.ref is None:
            self.ref = greyscale_frame.copy()
            return np.zeros_like(greyscale_frame, bool), np.zeros_like(greyscale_frame, bool)


        on = self.on_lookup[self.ref, greyscale_frame]
        off = self.off_lookup[self.ref, greyscale_frame]

        fired = on | off                    # Map showing which pixels fired, to update values
        self.ref[fired] = greyscale_frame[fired]

        return on, off
