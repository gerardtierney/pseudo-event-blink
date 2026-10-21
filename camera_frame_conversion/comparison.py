import time
import cv2
import numpy as np
import csv
from camera_frame_conversion.webcam_to_event import PseudoEventCamera

THRESHOLD_NL = 30
THRESHOLD = 0.2


file = "results.csv"
with open(file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Method", "Threshold","Resolution", "frame", "Average total time per frame", "Average frame conversion", "Theoretical fps"])

    #No log, pure subtraction no lookup average time calculator
    for i in range(5):
        cap = cv2.VideoCapture(r'C:\Users\gerar\OneDrive - National University of Ireland, Galway\Pictures\Camera Roll\EventComparisonFile.mp4')
        camera = PseudoEventCamera(THRESHOLD_NL)

        start_time = time.perf_counter()
        frame_count = 0
        step_elapsed_ms = 0


        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            t0 = time.perf_counter()

            greyscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Generate events and measure conversion time
            on, off = camera.step(greyscale_frame)
            frame_count += 1


            elapsed_ms = (time.perf_counter() - start_time) * 1000
            avg_ms = elapsed_ms / frame_count

            step_elapsed_ms += (time.perf_counter() - t0) * 1000
            avg_step_ms = step_elapsed_ms / frame_count

            # Display events: ON = red, OFF = blue
            events = np.zeros((*greyscale_frame.shape, 3), dtype=np.uint8)
            events[on] = (0, 0, 255)
            events[off] = (255, 0, 0)

            writer.writerow(["Subtraction",THRESHOLD_NL, greyscale_frame.shape, frame_count, round(avg_ms, 2), round(avg_step_ms,2), round( (1000 / avg_step_ms),2)])
        cap.release()



    # log lookup: np array of log values, logs are considered because log responds to relative change (contrast), and contrast belongs to the object, not the lighting.

    for i in range(5):
        cap = cv2.VideoCapture(r'C:\Users\gerar\OneDrive - National University of Ireland, Galway\Pictures\Camera Roll\EventComparisonFile.mp4')
        camera = PseudoEventCamera(THRESHOLD)

        start_time = time.perf_counter()
        frame_count = 0
        step_elapsed_ms = 0

        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            t0 = time.perf_counter()

            greyscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Generate events and measure conversion time
            on, off = camera.step(greyscale_frame)
            frame_count += 1

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            avg_ms = elapsed_ms / frame_count

            step_elapsed_ms += (time.perf_counter() - t0) * 1000
            avg_step_ms = step_elapsed_ms / frame_count

            # Display events: ON = red, OFF = blue
            events = np.zeros((*greyscale_frame.shape, 3), dtype=np.uint8)
            events[on] = (0, 0, 255)
            events[off] = (255, 0, 0)

            writer.writerow( ["Log Lookup", THRESHOLD_NL, greyscale_frame.shape, frame_count, round(avg_ms, 2), round(avg_step_ms, 2), round((1000 / avg_step_ms), 2)])
        cap.release()



print("done")
