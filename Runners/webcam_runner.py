import cv2
import numpy as np
import time

from Event_Conversion.conversion_log_1 import PseudoEventCamera
# from Event_Conversion.conversion_log_2 import PseudoEventCamera
# from Event_Conversion.conversion_log_3 import PseudoEventCamera
# from Event_Conversion.conversion_subtraction_1 import PseudoEventCamera
# from Event_Conversion.conversion_subtraction_2 import PseudoEventCamera

THRESHOLD = None # Leave as None for default values

# Blink detection: uncomment every line starting with "# BLINK:" to run it
# BLINK: from Blink_Detection.FaceDetection import blinkLocaterWrapper


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)  # 0 = webcam, or put a video file path here to test on a recording

    if THRESHOLD is not None:
        camera = PseudoEventCamera(THRESHOLD)
    else:
        camera = PseudoEventCamera()

    start_time = time.perf_counter()
    frame_count = 0
    step_elapsed_ms = 0

    # BLINK: fps = cap.get(cv2.CAP_PROP_FPS) or 30  # used to turn frame numbers into seconds, some webcams report 0 so fall back to 30
    # BLINK: print(f"FPS: {fps}")

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        t0 = time.perf_counter()

        greyscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # only needed for 1080p video, shrinks it to 640x360 so GRID = 20 fits (webcam is already 640x480):
        # greyscale_frame = cv2.resize(greyscale_frame, (640, 360), interpolation=cv2.INTER_AREA)

        # Generate events and measure conversion time
        on, off = camera.step(greyscale_frame)
        # BLINK: if frame_count == 0:
        # BLINK:     print(f"Resolution: {greyscale_frame.shape}")
        frame_count += 1

        # BLINK: if blinkLocaterWrapper(on, off):
        # BLINK:     print(f"Blink detected at {round(frame_count / fps, 1)} s (frame {frame_count})")


        elapsed_ms = (time.perf_counter() - start_time) * 1000
        avg_ms = elapsed_ms / frame_count

        step_elapsed_ms += (time.perf_counter() - t0) * 1000
        avg_step_ms = step_elapsed_ms / frame_count

        # Display events: ON = red, OFF = blue
        events = np.zeros((*greyscale_frame.shape, 3), dtype=np.uint8)
        events[on] = (0, 0, 255)
        events[off] = (255, 0, 0)

        cv2.putText(
            events,
            f"Average total time per frame: {avg_ms:.2f} ms",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )
        cv2.putText(
            events,
            f"Average frame conversion: {avg_step_ms:.2f} ms",
            (10, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )

        cv2.imshow("Webcam", frame)
        cv2.imshow("Events", events)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


    print(f"Threshold: {camera.threshold}")
    print(f"Webcam quality: {greyscale_frame.shape}")
    print(f"Frames processed: {frame_count}")
    print(f"Average total time per frame: {avg_ms:.2f} ms") # Slowed by webcam fps
    print(f"Average frame conversion: {avg_step_ms:.2f} ms")
    print(f"Theoretical fps: {1000 / avg_step_ms:.2f} fps")
