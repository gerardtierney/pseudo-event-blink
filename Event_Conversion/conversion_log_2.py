import numpy as np


def upper_thresh_int(n, threshold):
    if n == 0:
        return np.uint8(1)
    log_n = np.log(n)
    upper_log = log_n + threshold
    upper_bound = np.exp(upper_log)
    if upper_bound > 255:
        return np.uint8(255)
    else:
        return np.uint8(np.floor(upper_bound))

def lower_thresh_int(n, threshold):
    if n == 0:
        return np.uint8(1)
    log_n = np.log(n)
    lower_log = log_n - threshold
    lower_bound = np.exp(lower_log)
    if lower_bound > 255:
        return np.uint8(255)
    else:
        return np.uint8(np.floor(lower_bound))


class PseudoEventCamera:
    def __init__(self, threshold = 0.2):
        self.threshold = threshold
        self.ref = None
        self.upper_bound_lookup = np.array([upper_thresh_int(n, threshold) for n in range(256)], dtype=np.uint8)
        self.lower_bound_lookup = np.array([lower_thresh_int(n, threshold) for n in range(256)], dtype=np.uint8)


    def step(self, greyscale_frame):

        if self.ref is None:
            self.ref = greyscale_frame.copy()
            return np.zeros_like(greyscale_frame, bool), np.zeros_like(greyscale_frame, bool)

        threshold_on = self.upper_bound_lookup[self.ref]
        threshold_off = self.lower_bound_lookup[self.ref]

        on = greyscale_frame > threshold_on
        off = greyscale_frame < threshold_off

        fired = on | off                    # Map showing which pixels fired, to update values
        self.ref[fired] = greyscale_frame[fired]

        return on, off
