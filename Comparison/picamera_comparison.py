import time
import cv2
from picamera2 import Picamera2
import numpy as np
import csv
from Event_Conversion.conversion_log_1 import PseudoEventCamera as PseudoEventCamera
from Event_Conversion.conversion_log_2 import PseudoEventCamera as PseudoEventCamera2
from Event_Conversion.conversion_log_3 import PseudoEventCamera as PseudoEventCamera3
from Event_Conversion.conversion_subtraction_1 import PseudoEventCamera as PseudoEventCameraNL
from Event_Conversion.conversion_subtraction_2 import PseudoEventCamera as PseudoEventCameraNL2

THRESHOLD_NL = 30
THRESHOLD = 0.2

SHOW_UNPROCESSED = True
SHOW_EVENTS = True
FRAMERATE = 180  # 180 FPS likely will not be reached, chosen to force the algorithms to operate at maximum speed
FRAMEDURATION = 1000000 // FRAMERATE
EXPOSURE = min(round(FRAMEDURATION * 0.9), 20000) # 20ms unless framerate is faster, then open 90% of frame
FRAMEWIDTH = 640
FRAMEHEIGHT = 480


FRAMES_PER_TEST = 120


picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"format": "YUV420", "size": (FRAMEWIDTH, FRAMEHEIGHT)}
)

picam2.configure(config)

picam2.set_controls({
    "FrameDurationLimits": (FRAMEDURATION, FRAMEDURATION),
    "AeEnable": False,
    "ExposureTime": EXPOSURE,
    "AnalogueGain": 3.0,
    "AwbEnable": False,
    "ColourGains": (1.5, 1.2)
})

picam2.start()



def run_comparison(camera, method_name):
    full_frame = picam2.capture_array("main") # Ensure first frame doesnt cause delays
    brightness_data = full_frame[:FRAMEHEIGHT, :]

    on, off = camera.step(brightness_data)

    frame_count = 0
    start_time = time.perf_counter()

    while frame_count < FRAMES_PER_TEST:
        full_frame = picam2.capture_array("main")
        brightness_data = full_frame[:FRAMEHEIGHT, :]

        on, off = camera.step(brightness_data)

        events = np.zeros((*brightness_data.shape, 3), dtype=np.uint8)
        events[on] = (0, 0, 255)
        events[off] = (255, 0, 0)

        frame_count += 1

        if SHOW_UNPROCESSED:
            bgr_frame = cv2.cvtColor(full_frame, cv2.COLOR_YUV2BGR_I420)
            cv2.imshow("Camera Feed", bgr_frame)


        if SHOW_EVENTS:
            cv2.imshow("Events", events)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    elapsed = time.perf_counter() - start_time
    cv2.destroyAllWindows()

    avg_ms = elapsed / frame_count

    writer.writerow([method_name, camera.threshold, brightness_data.shape, frame_count, round(avg_ms, 2), round((1000 / avg_ms), 2), SHOW_UNPROCESSED, SHOW_EVENTS])




file = "picamera_results.csv"
try:
    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Method", "Threshold","Resolution", "frames", "Average time per frame", "FPS captured", "Unprocessed stream displayed", "Processed stream displayed"])

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

finally:
    picam2.stop()


print("done")