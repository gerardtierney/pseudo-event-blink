import time
import cv2
import numpy as np
import csv
from Event_Conversion.conversion_log_1 import PseudoEventCamera as PseudoEventCamera
from Event_Conversion.conversion_log_2 import PseudoEventCamera as PseudoEventCamera2
from Event_Conversion.conversion_log_3 import PseudoEventCamera as PseudoEventCamera3
from Event_Conversion.conversion_subtraction_1 import PseudoEventCamera as PseudoEventCameraNL
from Event_Conversion.conversion_subtraction_2 import PseudoEventCamera as PseudoEventCameraNL2

THRESHOLD_NL = 30
THRESHOLD = 0.2


def run_comparison(camera, method_name):
    cap = cv2.VideoCapture(r'EventComparisonFile.mp4')

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

    writer.writerow([method_name, camera.threshold, greyscale_frame.shape, frame_count, round(avg_ms, 2), round(avg_step_ms, 2),round((1000 / avg_step_ms), 2)])
    cap.release()



file = "mp4_results.csv"
with open(file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Method", "Threshold","Resolution", "frame", "Average total time per frame", "Average frame conversion", "Theoretical fps"])

    #No log, pure subtraction no lookup average time calculator
    for i in range(5):
        print("Sub1",i)
        run_comparison(PseudoEventCameraNL(THRESHOLD_NL), "Subtraction 1")

    # Log lookup: np array of log values, logs are considered because log responds to relative change (contrast), and contrast belongs to the object, not the lighting.
    for i in range(5):
        print("Log1", i)
        run_comparison(PseudoEventCamera(THRESHOLD), "Log 1")

    #No log, pure subtraction uint8
    for i in range(5):
        print("Sub2", i)
        run_comparison(PseudoEventCameraNL2(THRESHOLD_NL), "Subtraction 2")

    # log uint8 lookup
    for i in range(5):
        print("Log2", i)
        run_comparison(PseudoEventCamera2(THRESHOLD), "Log 2")

    # log 2D boolean lookup
    for i in range(5):
        print("Log3", i)
        run_comparison(PseudoEventCamera3(THRESHOLD), "Log 3")

print("done")
