import numpy as np

class BlinkDetector:
    def __init__(self,TILE_THRESHOLD = 0.06,GRID=20,MIN_GAP_FRAMES = 2,MAX_GAP_FRAMES = 16,REFRACTORY_FRAMES = 20,SPIKE_RATIO=2,AVG_DECAY = 0.95):
        self.TILE_THRESHOLD = TILE_THRESHOLD
        self.GRID = GRID
        self.MIN_GAP_FRAMES = MIN_GAP_FRAMES  # closing and opening bursts at least this far apart
        self.MAX_GAP_FRAMES = MAX_GAP_FRAMES  # closing and opening bursts at most this far apart
        self.REFRACTORY_FRAMES = REFRACTORY_FRAMES # wait this long after a blink before counting another
        self.frameCounter = 0
        self.potentialCoordinates = []
        self.prevBlinks = []
        self.onRef = None
        self.offRef = None
        self.SPIKE_RATIO = SPIKE_RATIO
        self.AVG_DECAY = AVG_DECAY



        # Function used to make sure eye geometries are in range, t states which type of geometry is being checked
    # 'c' = columns of two hot tiles (eye gap), 'r' = rows of two hot tiles (eyes level), 'p' = two bursts in the same place
    def inRange(self,a, b, t):

        if t == 'c' and b is not None:
            return 2 <= abs(a - b) <= 5

        elif t == 'r' and b is not None:
            return abs(a - b) <= 1

        elif t == 'p':
            # (X1,Y1,X2,Y2,Polarity,#Frame)

            # bursts need to be at least 2 frames apart, a real blink can't close and open in the same frame
            if (abs(a[-1] - b[-1]) >= self.MIN_GAP_FRAMES):

                if len(self.prevBlinks) > 0 and not ((a[-1] + b[-1]) / 2 > self.prevBlinks[-1][-1] + self.REFRACTORY_FRAMES):
                    return None

                else:
                    return (abs(a[0] - b[0]) <= 1) and (abs(a[1] - b[1]) <= 1) and (abs(a[2] - b[2]) <= 1) and (
                            abs(a[3] - b[3]) <= 1)

        return None

    # Takes our ON/OFF True false 2D arrays and turns them into a "gridbox"
    # - The array is first re shaped to allow the .sum() to combine certain values
    # - This is because we are splitting the frame into a grid, then we have the total number of events in that grid
    # - reshape means .sum() will sum in the shape of the tiles
    def frameToGridbox(self,arr):

        boxH, boxW = arr.shape
        boxH, boxW = boxH // self.GRID, boxW // self.GRID
        # view as (tiles down, rows in tile, tiles across, values in tile), sum inside each tile -> grid of counts per tile
        gridbox = arr.reshape(boxH, self.GRID, boxW, self.GRID).sum(axis=(1, 3))

        return gridbox



    # candidate tile coordinate generater from a given gridbox
    def blinkSearch(self,gridbox,ref):
        # here we will take the gridbox, then analyse the tiles in it, to search for bursts of opposite polarity events

        # gridbox / GRID**2 = fraction of the tile that fired; argwhere gives (row, column) of every tile over the threshold
        # tiles must also be a certain ratio above what their "normal" level has been, to reduce false positives
        potential_eyes = np.argwhere( (gridbox/(self.GRID ** 2) >= self.TILE_THRESHOLD) & (gridbox > ref * self.SPIKE_RATIO) )

        # a blink only lights up a few tiles, loads of hot tiles means head movement or lighting, so skip the frame
        if len(potential_eyes) >= 10:
            return None

        # compare every hot tile with every other one, first pair at eye spacing wins
        # (a tile against itself fails since its columns are 0 apart)
        # left eye (smaller column) always returned first, so two bursts of the same blink line up in the 'p' check
        for y, x in potential_eyes:
            for b, a in potential_eyes:
                if self.inRange(x, a, 'c') and self.inRange(y, b, 'r'):
                    if x<=a:
                        return x, y, a, b
                    else:
                        return a,b,x, y

        return None

    # polarity of the stored burst, None if nothing stored yet
    # (list never holds more than 1 entry when this gets called, so first = last)
    def prevPolarity(self,array):

        for i in array:
            return i[4]
        return None

    def blinkLocaterWrapper(self,on, off):


        self.frameCounter += 1

        onBox = self.frameToGridbox(on)
        offBox = self.frameToGridbox(off)


        if self.onRef is None:
            self.onRef = np.zeros(onBox.shape, dtype=np.float32)

        if self.offRef is None:
            self.offRef = np.zeros(offBox.shape, dtype=np.float32)

        onBlink = self.blinkSearch(onBox,self.onRef)
        offBlink = self.blinkSearch(offBox,self.offRef)

        self.offRef = self.AVG_DECAY * self.offRef + (1 - self.AVG_DECAY) * offBox
        self.onRef = self.AVG_DECAY * self.onRef + (1 - self.AVG_DECAY) * onBox

        if onBlink is not None:
            onBlink = (*onBlink, 1, self.frameCounter)
        if offBlink is not None:
            offBlink = (*offBlink, 0, self.frameCounter)

        # on/offBlink format is now (X1,Y1,X2,Y2,Polarity,#Frame)

        # a moving eyelid makes ON and OFF in the same frame, so either can be stored,
        # just never the same polarity twice in a row, so stored bursts always alternate
        if (onBlink) and self.prevPolarity(self.potentialCoordinates) != 1:
            self.potentialCoordinates.append(onBlink)
        elif (offBlink) and self.prevPolarity(self.potentialCoordinates) != 0:
            self.potentialCoordinates.append(offBlink)

        # throw away bursts older than MAX_GAP_FRAMES, too long ago to be the same blink
        # (loops over a copy so removing doesn't skip entries)
        for entry in list(self.potentialCoordinates):
            if (self.frameCounter - entry[-1]) > self.MAX_GAP_FRAMES:
                self.potentialCoordinates.remove(entry)

        if len(self.potentialCoordinates) == 2:

            if self.inRange(self.potentialCoordinates[0], self.potentialCoordinates[1], 'p'):
                # save both bursts as one blink, then clear so the same blink isn't counted again
                self.prevBlinks.append((*self.potentialCoordinates[0], *self.potentialCoordinates[1]))
                self.potentialCoordinates.clear()
                return self.prevBlinks[-1]

            else:
                # no match, drop the older burst and keep the newer one for the next frames
                self.potentialCoordinates.pop(0)

        return None





