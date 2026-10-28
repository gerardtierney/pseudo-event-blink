import time
import cv2
from picamera2 import Picamera2
import numpy as np

# Event camera code from webcam
THRESHOLD = 0.2
SHOW_UNPROCESSED = False
FRAMERATE = 30
FRAMEDURATION = 1000000 // FRAMERATE
EXPOSURE = min(round(FRAMEDURATION * 0.9), 20000) # 20ms unless framerate is faster, then open 90% of frame
FRAMEWIDTH = 640
FRAMEHEIGHT = 480

class PseudoEventCamera:
    def __init__(self, threshold):
        self.threshold = threshold
        self.ref = None



    def step(self, greyscale_frame):
        brightness = np.int16(greyscale_frame)

        if self.ref is None:
            self.ref = brightness.copy()
            return np.zeros_like(greyscale_frame, bool), np.zeros_like(greyscale_frame, bool)

        change = brightness - self.ref      # Vectorization

        on = change >= self.threshold
        off = change <= -self.threshold

        fired = on | off                    # Map showing which frames changed, to update values
        self.ref[fired] = brightness[fired]

        return on, off


if __name__ == "__main__":

    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"format": "YUV420", "size": (FRAMEWIDTH, FRAMEHEIGHT)}
    )


    picam2.configure(config)

    picam2.set_controls({
        "FrameDurationLimits": (FRAMEDURATION, FRAMEDURATION),
        "AeEnable": False,
        "ExposureTime": EXPOSURE,
        "AnalogueGain": 1.0,
        "AwbEnable": False,
        "ColourGains": (1.5, 1.2)
    })

    picam2.start()
    camera = PseudoEventCamera(THRESHOLD)

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            full_frame = picam2.capture_array("main")
            brightness_data = full_frame[:FRAMEHEIGHT, :]

            on, off = camera.step(brightness_data)

            events = np.zeros((*brightness_data.shape, 3), dtype=np.uint8)
            events[on] = (0, 0, 255)
            events[off] = (255, 0, 0)

            frame_count += 1
            if frame_count % FRAMERATE == 0:
                elapsed = time.time() - start_time
                print(f"Captured {frame_count} frames. Current operational FPS: {frame_count / elapsed:.2f}")

            if SHOW_UNPROCESSED:
                bgr_frame = cv2.cvtColor(full_frame, cv2.COLOR_YUV2BGR_I420)
                cv2.imshow("Camera Feed", bgr_frame)

            cv2.imshow("Events", events)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cv2.destroyAllWindows()





    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        picam2.stop()
