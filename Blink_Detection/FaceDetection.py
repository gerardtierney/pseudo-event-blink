import numpy as np


THRESHOLD_NL = 5
TILE_THRESHOLD = 0.05
GRID = 20
MIN_GAP_FRAMES = 2       # closing and opening bursts at least this far apart
MAX_GAP_FRAMES = 12          # closing and opening bursts at most this far apart
REFRACTORY_FRAMES = 20   # wait this long after a blink before counting another


frameCounter = 0
potentialCoodinates = []
prevBlinks = []


#Function used to make sure eye geometries are in range, t states which type of geometry is being checked
# 'c' = columns of two hot tiles (eye gap), 'r' = rows of two hot tiles (eyes level), 'p' = two bursts in the same place
def inRange(a,b,t):

    if t == 'c' and b is not None:
        return 2 <= abs(a - b) <= 5

    elif t == 'r' and b is not None:
        return abs(a-b) <=1

    elif t == 'p':
        #(X1,Y1,X2,Y2,Polarity,#Frame)

        # bursts need to be at least 2 frames apart, a real blink can't close and open in the same frame
        if (abs(a[-1] - b[-1]) >= MIN_GAP_FRAMES):

            if len(prevBlinks) > 0 and  not ((a[-1] + b[-1])/ 2 > prevBlinks[-1][-1] + REFRACTORY_FRAMES):
                return None

            else :
                return (abs(a[0] - b[0]) <= 1) and (abs(a[1] - b[1]) <= 1) and (abs(a[2] - b[2]) <= 1) and (
                        abs(a[3] - b[3]) <= 1)




    return None

#candidate tile coodinate generater from a given gridbox
def blinkSearch(gridbox):

    #here we will take the gridbox, then analyse the tiles in it, to search for bursts of opposite polarity events

    # count / GRID**2 = fraction of the tile that fired; argwhere gives (row, column) of every tile over the threshold
    potential_eyes = np.argwhere((gridbox / (GRID**2)) >= TILE_THRESHOLD)

    # a blink only lights up a few tiles, loads of hot tiles means head movement or lighting, so skip the frame
    if len(potential_eyes) >=10:
        return None



    # compare every hot tile with every other one, first pair at eye spacing wins
    # (a tile against itself fails since its columns are 0 apart)
    # TODO: pair can come back as (right eye, left eye), make it always return the left eye first
    for y,x in potential_eyes:
            for b,a in potential_eyes:
                if inRange(x,a,'c') and inRange(y,b,'r'):
                    return x,y,a,b

    return None


#Takes our ON/OFF True false 2D arrays and turns them into a "gridbox"
# - The array is first re shaped to allow the .sum() to combine certain values
# - This is because we are splitting the frame into a grid, then we have the total number of events in that grid
# - reshape means .sum() will sum in the shape of the tiles
def frameToGridbox(arr):

    boxH,boxW = arr.shape
    boxH, boxW = boxH//GRID ,boxW//GRID
    # view as (tiles down, rows in tile, tiles across, values in tile), sum inside each tile -> grid of counts per tile
    gridbox = arr.reshape(boxH,GRID,boxW,GRID).sum(axis=(1,3))

    return gridbox


# polarity of the stored burst, None if nothing stored yet
# (list never holds more than 1 entry when this gets called, so first = last)
def prevPolarity(array):

    for i in array:
        return i[4]
    return None


def blinkLocaterWrapper(on,off):

    global frameCounter
    global potentialCoodinates

    frameCounter +=1


    onBox = frameToGridbox(on)
    offBox = frameToGridbox(off)

    onBlink = blinkSearch(onBox)
    offBlink = blinkSearch(offBox)

    if onBlink is not None:
        onBlink = (*onBlink,1, frameCounter)
    if offBlink is not None:
        offBlink = (*offBlink,0, frameCounter)

    #on/offBlink format is now (X1,Y1,X2,Y2,Polarity,#Frame)

    # a moving eyelid makes ON and OFF in the same frame, so either can be stored,
    # just never the same polarity twice in a row, so stored bursts always alternate
    if (onBlink) and prevPolarity(potentialCoodinates) != 1:
        potentialCoodinates.append(onBlink)
    elif (offBlink) and prevPolarity(potentialCoodinates) != 0:
        potentialCoodinates.append(offBlink)

    # throw away bursts older than MAX_GAP_FRAMES, too long ago to be the same blink
    # (loops over a copy so removing doesn't skip entries)
    for entry in list(potentialCoodinates):
        if (frameCounter - entry[-1]) > MAX_GAP_FRAMES:
            potentialCoodinates.remove(entry)

    if len(potentialCoodinates) == 2:


        if inRange(potentialCoodinates[0],potentialCoodinates[1],'p'):
            # save both bursts as one blink, then clear so the same blink isn't counted again
            prevBlinks.append((*potentialCoodinates[0],*potentialCoodinates[1]))
            potentialCoodinates.clear()
            return prevBlinks[-1]

        else :
            # no match, drop the older burst and keep the newer one for the next frames
            potentialCoodinates.pop(0)

    return None


