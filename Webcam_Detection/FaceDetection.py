from Webcam_Event_Conversion.webcam_to_event_NoLog import *

THRESHOLD_NL = 5

cap = cv2.VideoCapture(r'C:\Users\gerar\OneDrive - National University of Ireland, Galway\Pictures\Camera Roll\EventComparisonFile.mp4')
camera = PseudoEventCameraNL(THRESHOLD_NL)


def blinkSearch(gridbox):

    #here we will take the gridbox, then anayylse the tiles in it, to search for bursts of opposite polarity events
    return



def frameToGridbox(arr,grid):

    boxW,boxL = (arr.shape)/grid #gets the gridboxes dimensions from grids size
    gridbox = arr.reshape(boxL,grid,boxW,grid).sum(axis=(1,3))

    return gridbox



while cap.isOpened():
    ok, frame = cap.read()
    if not ok:
        break
    t0 = time.perf_counter()
    greyscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Generate events and measure conversion time
    on, off = camera.step(greyscale_frame)
    deltaTime = time.perf_counter() - t0
