import numpy as np

class Picamera2:

    def __init__(self, seed = None):
        self.FRAMEWIDTH = None
        self.FRAMEHEIGHT = None
        self.previous_y = None
        self.previous_uv = None
        self.rng = np.random.default_rng(seed)

    def create_video_configuration(self, main=None):
        return main

    def configure(self, config):
        self.FRAMEWIDTH, self.FRAMEHEIGHT = config["size"]

    def set_controls(self, controls):
        pass

    def start(self):
        self.previous_y = self.rng.integers(100, 150, size=(self.FRAMEHEIGHT, self.FRAMEWIDTH), dtype=np.uint8)
        self.previous_uv = self.rng.integers(100, 150, size=(self.FRAMEHEIGHT // 2, self.FRAMEWIDTH), dtype=np.uint8)

    def capture_array(self, name="main"):
        random_change = self.rng.integers(-4, 5, size=(self.FRAMEHEIGHT, self.FRAMEWIDTH)).astype('uint8')
        random_limiter = self.rng.random(random_change.shape) < 0.25
        self.previous_y += (random_change * random_limiter)
        return np.concatenate((self.previous_y, self.previous_uv), axis=0)


    def stop(self):
        pass