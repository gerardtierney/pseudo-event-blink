import numpy as np

class Picamera2:

    def __init__(self, seed = None):
        self.FRAMEWIDTH = None
        self.FRAMEHEIGHT = None
        self.previous = None
        self.rng = np.random.default_rng(seed)

    def create_video_configuration(self, main=None):
        return main

    def configure(self, config):
        self.FRAMEWIDTH, height = config["size"]
        self.FRAMEHEIGHT = int(height * 1.5)

    def set_controls(self, controls):
        pass

    def start(self):
        self.previous = self.rng.integers(100, 150, size=(self.FRAMEHEIGHT, self.FRAMEWIDTH), dtype=np.uint8)

    def capture_array(self, name="main"):
        random_change = self.rng.integers(-4, 5, size=(self.FRAMEHEIGHT * 2 // 3, self.FRAMEWIDTH)).astype('uint8')
        random_limiter = self.rng.random(random_change.shape) < 0.25
        self.previous[:self.FRAMEHEIGHT * 2 // 3] += (random_change * random_limiter)
        return self.previous


    def stop(self):
        pass