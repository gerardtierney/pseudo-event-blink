import cv2
import numpy as np
import time

THRESHOLD = 0.2

def upper_thresh_int(n, threshold):
    if n == 0:
        return np.uint8(1)
    log_n = np.log(n)
    upper_log = log_n + threshold
    upper_bound = np.exp(upper_log)
    if upper_bound > 255:
        return np.uint8(255)
    else:
        return np.uint8(np.floor(upper_bound))

def lower_thresh_int(n, threshold):
    if n == 0:
        return np.uint8(1)
    log_n = np.log(n)
    lower_log = log_n - threshold
    lower_bound = np.exp(lower_log)
    if lower_bound > 255:
        return np.uint8(255)
    else:
        return np.uint8(np.floor(lower_bound))


class PseudoEventCamera2:
    def __init__(self, threshold):
        self.threshold = threshold
        self.ref = None
        self.upper_bound_lookup = np.array([upper_thresh_int(n, threshold) for n in range(256)], dtype=np.uint8)
        self.lower_bound_lookup = np.array([lower_thresh_int(n, threshold) for n in range(256)], dtype=np.uint8)


    def step(self, greyscale_frame):

        if self.ref is None:
            self.ref = greyscale_frame.copy()
            return np.zeros_like(greyscale_frame, bool), np.zeros_like(greyscale_frame, bool)

        threshold_on = self.upper_bound_lookup[self.ref]
        threshold_off = self.lower_bound_lookup[self.ref]

        on = greyscale_frame > threshold_on
        off = greyscale_frame < threshold_off

        fired = on | off                    # Map showing which pixels fired, to update values
        self.ref[fired] = greyscale_frame[fired]

        return on, off


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    camera = PseudoEventCamera2(THRESHOLD)

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


    print(f"Logaritmic threshold: {THRESHOLD}")
    print(f"Webcam quality: {greyscale_frame.shape}")
    print(f"Frames processed: {frame_count}")
    print(f"Average total time per frame: {avg_ms:.2f} ms") # Slowed by webcam fps
    print(f"Average frame conversion: {avg_step_ms:.2f} ms")
    print(f"Theoretical fps: {1000 / avg_step_ms:.2f} fps")
