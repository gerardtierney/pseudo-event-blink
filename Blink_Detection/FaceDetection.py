import cv2
import numpy as np
import time

from Event_Conversion.conversion_subtraction_1 import PseudoEventCamera

THRESHOLD_NL = 5
TILE_THRESHOLD = 0.15
GRID = 60
MAX_FRAMES = 12

cap = cv2.VideoCapture(r'C:\Users\gerar\OneDrive - National University of Ireland, Galway\Pictures\Camera Roll\EventComparisonFile.mp4')
camera = PseudoEventCamera(THRESHOLD_NL)
frameCounter = 0
potentialCoodinates = []



def inRange(a,b):
    # TODO: 2 to 5 apart suits the column gap between two eyes, but rows should be 0 to 1 apart,
    #       and matching a burst with its opposite burst needs "same place" (0 to 1 apart)
    return abs(a-b) >=2 and abs(a-b) <=5




def blinkSearch(gridbox):

    #here we will take the gridbox, then analyse the tiles in it, to search for bursts of opposite polarity events

    # count / GRID**2 = fraction of the tile that fired; argwhere gives (row, column) of every tile over the threshold
    potential_eyes = np.argwhere((gridbox / (GRID**2)) >= TILE_THRESHOLD)

    # TODO: starting at -3 can fake a match with a hot tile near the top-left corner
    xPrev = -3
    yPrev = -3

    for y,x in potential_eyes:

        # TODO: only compares each hot tile with the one just before it in the list, so other pairs are missed
        if inRange(x,xPrev) and inRange(y,yPrev):
            return x,y,xPrev,yPrev
        else:
            xPrev = x
            yPrev = y

    return None



def frameToGridbox(arr):

    boxH,boxW = arr.shape
    boxH, boxW = boxH//GRID ,boxW//GRID
    # view as (tiles down, rows in tile, tiles across, values in tile), sum inside each tile -> grid of counts per tile
    gridbox = arr.reshape(boxH,GRID,boxW,GRID).sum(axis=(1,3))

    return gridbox



def blinkLocaterWrapper(on,off):

    global frameCounter
    global potentialCoodinates

    frameCounter +=1

    valid = 1
    onBox = frameToGridbox(on)
    offBox = frameToGridbox(off)

    onBlink = blinkSearch(onBox)
    offBlink = blinkSearch(offBox)

    if onBlink is not None:
        onBlink = (*onBlink, frameCounter)
    if offBlink is not None:
        offBlink = (*offBlink, frameCounter)

    # TODO: doesn't check ON then OFF order, two bursts of the same polarity would also pair
    if onBlink and not offBlink:
        potentialCoodinates.append(onBlink)
    elif offBlink and not onBlink:
        potentialCoodinates.append(offBlink)

    for entry in list(potentialCoodinates):
        if (frameCounter - entry[-1]) > MAX_FRAMES:
            potentialCoodinates.remove(entry)

    if len(potentialCoodinates) == 2:
        for i in range(len(potentialCoodinates[0])-1):
            if not (inRange(potentialCoodinates[0][i],potentialCoodinates[1][i])):
                valid = 0

        if valid:
            # TODO: list isn't cleared after a match, so the same blink is reported every frame after
            return potentialCoodinates

        elif len(potentialCoodinates) >= 1:
            potentialCoodinates.pop(0)

    # TODO: no minimum gap between the two bursts yet (a real blink needs at least ~2 frames)

    return None



if __name__ == "__main__":
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        t0 = time.perf_counter()
        greyscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Generate events and measure conversion time
        on, off = camera.step(greyscale_frame)
        deltaTime = time.perf_counter() - t0
        if blinkLocaterWrapper(on,off):
            print("Blink detected!")
